from openai import OpenAI
import os

client = OpenAI(os.getenv("API_KEY"))

async def generate_pandas_code(query, df):
    # summarize df
    info = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
    }
    prompt = f"""You are a data analyst. Generate Python pandas code or matplotlib code to answer the user's question about a DataFrame.
    DataFrame info: {info}
    User question: {query}

    Requirements:
    1. The DataFrame is available as variable 'df'
    2. If a plot is needed, use matplotlib (plt) and do not call plt.show() at the end.
    3. Generate ONLY executable Python code, no explanations
    4. Store numerical results only (int, float etc) in variable 'result'.
    5. Use proper methods and error handling.
    6. Import numpy always as np always.
    """


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    generated_code = response.choices[0].message.content

    # Clean code (remove markdown formatting)
    if "```python" in generated_code:
        generated_code = generated_code.split("```python")[1].split("```")[0]
    elif "```" in generated_code:
        generated_code = generated_code.split("```")[1].split("```")[0]
    
    code = generated_code.strip()


    return code
