import pandas as pd
# import matplotlib.pyplot as plt
import io
import base64

def execute_code(code: str, df: pd.DataFrame):
    safe_globals = {"pd": pd}
    safe_locals = {"df": df.copy()}

    output = {"result": None, "image": None, "error": None}
    

    try:

        exec(code, safe_globals, safe_locals)
        plt = safe_locals.get("plt")

        

        if plt:
            figs = [plt.figure(n) for n in plt.get_fignums()]
            buf = io.BytesIO()
            figs[-1].savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            output["image"] = img_base64 
            plt.close("all")
        
        # Safely extract result: Coerce scalars to strings to avoid downstream iteration errors
        x = safe_locals.get("result")
        print(x)
       
        # Convert DataFrame/Series to dict (for JSON serialization)
        if hasattr(x, "to_dict"):
            output["result"] = x.to_dict()
        else:
            output["result"] = str(x)

    except TimeoutError:
        return {output["error"]: "Code execution timed out"}

    except Exception as e:
        output["error"]=str(e)


    return output
