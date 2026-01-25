# Measure-AI-Drift

## This project aims at testing souvereign LLMs in therapeutic context against propietary systems focusing on stochastic drift and consistency.


flowchart LR
    subgraph GenStack [Generation Stack - Synthetic Data]
        P[Patient LLM] <--> R[Router LLM]
        R --> T1[Therapist LLM]
        T1 <--> P
    end
    
    subgraph EvalStack [Evaluation Stack - Rescripting Only]
        FH[Frozen History] --> T2[Therapist LLM]
        SP[Stage Prompt Injected] --> T2
        T2 --> Plan[Plan Output]
        T2 --> Resp[Response Output]
    end
    
    GenStack -->|produces| D[Dialogues]
    D -->|sliced at rescripting entry| FH