To use benchmark you should install ollama and pull gemma3.
Ollama (https://ollama.com/download)
```
ollama pull gemma3
ollama run gemma3
```

Before using benchmark you need to install requirements.txt.
Then you launch api in first console
```
cd problem-solver/py/api
uvicorn main:app --reload
```
And then app in second console
```
cd problem-solver/py/app
streamlit run streamlit_app.py
```
Finally in third console launch benchmark
```
cd problem-solver/py
python benchmark/benchmark_eval.py
```

Benchmark uses .json file with questions in example `test.json`.

Answer is saving evaluate result in `triad_extended_results.json` by default.
