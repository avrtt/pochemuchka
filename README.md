<p>
    <span style="text-align: left">
      ver. 1.1.12&nbsp; •&nbsp; <u>Documentation</u> <b>(WIP)</b>: <b><a href="https://github.com/avrtt/pochemuchka/blob/main/documentation/en.md">🇺🇸 EN</a></b> | <b><a href="https://github.com/avrtt/pochemuchka/blob/main/documentation/ru.md">🇷🇺 RU</a></b>  
    </span>
    <span style="float: right">
        <b><a href="https://github.com/avrtt/pochemuchka/blob/main/documentation/commands.md">Commands</a></b>&nbsp; •&nbsp; <b><a href="https://github.com/avrtt/pochemuchka/blob/main/documentation/styles.md">Styles</a></b>&nbsp; •&nbsp; <b><a href="https://github.com/avrtt/pochemuchka/blob/main/documentation/conventions.md">Conventions</a></b>
    </span>
</p>

<br/>

This is an all-in-one library built as part of my other SaaS project. It provides various techniques for managing, optimizing and testing prompts for LLMs in both production and research environments. With the client's permission, this demo illustrates a system designed to dynamically integrate data, monitor performance metrics such as latency and cost, and efficiently balance loads among various AI models.

The system can help to simplify the development and testing of prompt-based interactions with LLMs. By combining real-time monitoring, dynamic caching and integration across multiple models, it offers tools for understanding the capabilities of AI-driven solutions. You can refine your prompt design or automatically adapt learning systems to evolving contexts.

> [!TIP] 
> Check out some simple usage examples in **[examples/getting_started.ipynb](https://github.com/avrtt/pochemuchka/blob/main/examples/getting_started.ipynb)**

Some features:
- **Dynamic prompt crafting**  
  Adapt and update prompts on the fly, ensuring you avoid issues like budget overflows by integrating live data.
- **Multi-model compatibility**  
  Easily switch between various LLM providers, distributing workload intelligently based on configurable weights.
- **Real-time performance insights**  
  Gain immediate visibility into metrics such as latency, token usage and overall cost.
- **CI/CD testing**  
  Automatically generate and execute tests during prompt calls by comparing responses with an ideal output provided by a human expert.
- **Efficient prompt caching**   
  Leverage a caching system with a short TTL (Time-To-Live) of five minutes to ensure that prompt content is always current while minimizing redundant data fetches.
- **Asynchronous interaction logging**  
  Log detailed interaction data in the background so that your application's performance remains unaffected.
- **User feedback integration**  
  Enhance prompt quality continuously by incorporating explicit feedback and ideal answers for previous responses.

## Architecture

The demo implements a smart caching mechanism with some lifespan for each prompt. This includes automatic refresh (every prompt call checks for an updated version from the server, ensuring that the cached version is always fresh), local backup (in case the central service is unavailable, the system reverts to a locally stored version of the prompt) and version synchronization (to maintain consistent versions across both local and remote environments).

The system supports two distinct methods for creating tests to ensure the quality of prompt outputs: inline and explicit. The first one includes test data with an ideal response during the LLM call, which automatically triggers test creation. The second invokes a test creation method for a given prompt directly, to compare the LLM's response against a predefined ideal answer.

Logs interact asynchronously, so logging happens in the background without impacting response times. You can automatically capture details like response latency, token count and associated costs, store complete snapshots of prompts, context and responses for analysis.

Feedback is integral to continuous improvement. You can attach ideal answers to previous responses, prompting the system to generate new tests and refine prompt formulations.

## License
MIT