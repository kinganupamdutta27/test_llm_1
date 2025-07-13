if __name__=="__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    from langchain.chat_models import init_chat_model

    llm = init_chat_model(
        model="gpt-4o",
        model_provider="openai",
        temperature=0.7,
        max_tokens=1000,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )


    print(llm.invoke("What is the capital of France?").content)

    