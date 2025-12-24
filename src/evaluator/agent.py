from langchain.agents import create_agent
from langchain_openai import ChatOpenAI 
from src.config import settings 
from src.schemas import EvaluationScore, AgentResponse
from langchain.tools import tool
from langchain.messages import HumanMessage
from src.config import settings


class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.openrouter_url,
            api_key=settings.openrouter_api_key,
            model=settings.llm, 
            temperature=0
        )
        # Define tool inside the constructor (so it can access self.llm and there's no error with @tool decorator)
        @tool("evaluate_prompt")
        def evaluate_prompt(prompt_content: str, 
                            query: str, 
                            rag_ans: str, 
                            correct_answer: str,
                            context: str) -> str:
                """
                Evaluates the quality of a RAG-generated answer against a user query,
                a gold (correct) answer, and the provided context.

                Input Arguments:
                - prompt_content (str): The instruction or prompt used to generate the RAG answer.
                - query (str): The original user question.
                - rag_ans (str): The answer produced by the RAG system.
                - correct_answer (str): The expected or gold-standard answer.
                - context (str): The retrieved or supporting context provided to the RAG system.

                Evaluation Metrics:
                - Faithfulness (0–1): Measures whether the RAG answer strictly adheres to the given context
                without hallucinations or unsupported claims.
                - Context Relevancy (0–1): Measures how relevant the provided context is for answering the query.
                - Answer Relevancy (0–1): Measures how well the RAG answer addresses the user query
                compared to the correct answer.

                Expected Response:
                - Returns the string "pass" if all metric scores meet or exceed predefined thresholds.
                - Returns the string "fail" otherwise.
                """

                evaluation_prompt = f"""
                You are an expert RAG evaluation model.

                Your task is to evaluate the quality of a Retrieval-Augmented Generation (RAG)
                answer using three metrics: Faithfulness, Context Relevancy, and Answer Relevancy.

                You are given the following inputs:

                ---
                Prompt Content:
                {prompt_content}

                User Query:
                {query}

                RAG Answer:
                {rag_ans}

                Correct Answer (Gold Standard):
                {correct_answer}

                Provided Context:
                {context}
                ---

                ### Evaluation Guidelines

                You MUST output numeric scores between 0.0 and 1.0 for each metric.

                #### 1. Faithfulness
                Score how strictly the RAG Answer is grounded in the Provided Context.
                - 1.0 → All claims are directly supported by the context.
                - 0.5 → Some claims are implied but not clearly stated.
                - 0.0 → Contains hallucinations or unsupported information.

                Do NOT use outside knowledge.

                #### 2. Context Relevancy
                Score how useful and relevant the Provided Context is for answering the User Query.
                - 1.0 → Context directly supports answering the query.
                - 0.5 → Context is partially relevant or incomplete.
                - 0.0 → Context is irrelevant.

                Judge the context itself, not the answer.

                #### 3. Answer Relevancy
                Score how well the RAG Answer addresses the User Query compared to the Correct Answer.
                - 1.0 → Fully answers the query correctly and clearly.
                - 0.5 → Partially answers or misses key details.
                - 0.0 → Incorrect or unrelated answer.

                ### Output Rules
                - Return ONLY structured output matching the EvaluationScore schema.
                - Do NOT include explanations, reasoning steps, or extra text.
                """
                faithfulness_thres = 0.7
                conext_relevancy_thres = 0.7
                answer_relevancy_thres = 0.7 

                # Get structured output for evaluation scores
                evaluator = self.llm.with_structured_output(EvaluationScore)
                scores = evaluator.invoke(evaluation_prompt)
                
                # Compare with thresholds to determine pass/fail
                if (scores.faithfulness >= faithfulness_thres and
                    scores.context_relevancy >= conext_relevancy_thres and
                    scores.answer_relevancy >= answer_relevancy_thres):
                    return "pass"
                else:
                    return "fail"
            
        self.tools = [evaluate_prompt]

        # Define system prompt for the agent
        self.prompt = """
        You are an evaluation agent responsible for assessing RAG answer quality.

        ### Core Responsibilities
        - Determine whether the provided RAG answer passes evaluation criteria.
        - Use the evaluation tool when sufficient inputs are provided.
        - Produce a final structured response using the AgentResponse schema.

        ### Tool Usage Rules
        - Always call the `evaluate_prompt` tool when the user provides:
        prompt_content, query, rag_ans, correct_answer, and context.
        - Do NOT attempt to evaluate manually without the tool.
        - Call the tool exactly once per evaluation request.
        - Do NOT modify or reinterpret user-provided inputs.

        ### Decision Logic
        - Rely exclusively on the tool's returned result ("pass" or "fail").
        - Do not override or reinterpret evaluation scores.
        - Do not add commentary or explanations outside the schema.

        ### Response Handling
        - Always return a structured AgentResponse.
        - Set `quality` to the tool result.
        - Keep responses concise and deterministic.

        You are optimized for correctness, consistency, and efficient tool orchestration.
        """

        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.prompt,
            response_format=AgentResponse
        )

    # Evaluation method 
    def evaluate(self, prompt_content: str, query: str, rag_ans: str, correct_answer: str, context: str) -> str:
        human_message = HumanMessage(
            content=f"""Evaluate the prompt with the following details:
            Prompt Content: {prompt_content}
            Query: {query}
            RAG Answer: {rag_ans}
            Correct Answer: {correct_answer}
            Context: {context}"""
        )
        for step in self.agent.stream({"messages": [human_message]},
                                      stream_mode="values"):
            step["messages"][-1].pretty_print()
        final_response = step["messages"][-1].content
        return final_response
    
      
agent = EvaluatorAgent()
resp=agent.evaluate(prompt_content="Provide a good response to the query based on the context.",
               query="How can I book a hotel room?",
               rag_ans="You need to call the hotel directly to make a reservation. Online booking is not available.",
               correct_answer="You can book a hotel room through our website by selecting your destination, dates, and preferred room type, then completing the payment process. ",
               context="Sample context")
