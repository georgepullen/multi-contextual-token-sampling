### **This methodology has been superseded by [Batched Multi-Contextual Token Sampling](https://github.com/georgepullen/batched-multi-contextual-token-sampling).**
***
# Multi-Contextual Token Sampling
A novel methodology for improving the needle in a haystack capabilities of chat SLMs.


![mcts](https://github.com/georgepullen/multi-contextual-token-sampling/assets/90179633/5fd24654-e5e9-4ed6-8cb3-0cd285e4fbcc)

### The Method
***
* Each context window of previous messages responds as if it is the sole context
* The highest probability next token **across all context windows** is sampled
* Each context window is concatenated with the **same next token**
* Only tokens that have appeared in previous chat logs can be used in the response
* This gives the agent the ability to **adapt to the users vocabulary** and style of conversation overtime

### Justification
***
Small Language Models struggle to generate accurate responses in long-context settings, such as chat modelling. With this novel methodology, the logits for the next token are computed for each chunk of context separately. Furthermore, the masking of unseen tokens further increases accuracy, particularly with respect to information such as dates and times.
