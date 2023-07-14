# Corpusaige
_Corpusaige_ is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.

__note__: this README is an excersise in [README Driven Development](https://tom.preston-werner.com/2010/08/23/readme-driven-development.html) or otherwise stated: until further notice the README does promise things which are not as yet implemented. Once the implementaion becomes more then a jumbled mess of ugly code that's likely not going to work, this notice will be removed. 
 
## Introduction
Corpusaige provides a powerful capability for system analysts and developers, aiding in the aggregation of an expansive collection of related document sets and complex source code pertinent to a specific system or domain. By bridging the gap between this collective information (termed the Corpus) and AI Large Language Models (LLMs), Corpusaige facilitates an insightful, AI-aided analysis, granting an holistic view of the project or system at hand.

This library embodies an iterative approach to knowledge refinement. It enables users to supplement the Corpus with additional metadata, introduce new information, and incorporate the AI's analysis results back into the system. This iterative enhancement to the Corpus significantly increases the precision and depth of the system's understanding, fostering a dynamic, ever-evolving model that encapsulates all relevant system or domain information.

![CorpuSaige: A Python utility library and tool for deep exploration and understanding of large document sets and source code](corpusaige.png)

## Features
__Incremental Knowledge Refinement__: Corpusaige incorporates an iterative process to enhance the depth and precision of system understanding, allowing the Corpus to dynamically evolve with added metadata, new information, and AI-analyzed results.

__Interface to a Large Language Model (LLM)__: Corpusaige functions as the primary interface to AI Large Language Models (LLMs), facilitating insightful, AI-powered system analysis.

__Support for Multiple Document Types__: Corpusaige inherently supports PDF and text files, with an extensible design that permits the addition of other document types, such as Word or Excel, without necessitating modifications to the core library.

__Local and Cloud-Based Vector Data Storage__: Corpusaige accommodates both local and cloud-based vector data storage, offering flexibility for debugging and scalability needs respectively.

__Compatibility with Notebook Environments__: As a Python library, Corpusaige is compatible with Jupyter or comparable notebook environments, enabling seamless incorporation into diverse workflows.

__Versatile CLI Tool__: Corpusaige can operate as a CLI tool, offering two modes: a batch command mode for document indexing and vector database storage, and a REPL mode for ad-hoc interactive sessions with the LLM about the Corpus.

__Plugin for Visual Studio__: Corpusaige can be used through a simple plugin for Visual Studio Code, allowing the user to use the tooling and directly navigate to the relevant documents in the active projects (workspace) related with the Corpus.

__Fully Configurable__: CorpuSaige's configurability extends to its usage as either a library or a CLI tool, permitting customization of the dataset, API key, vector database, and type of LLM.

## Use Case: Navigating and Enhancing a Complex Software System
Picture this: you're a software engineer who's recently joined a new team. Your responsibility? Maintaining and augmenting a sophisticated, legacy software system. This system is expansive and rather cryptic, characterized by scattered documentation across numerous sources and dense, intricate source code. To unravel this enigma and grasp the system thoroughly, you'd leverage Corpusaige.

Initially, your task is to compile all available documentation associated with the software system. This compilation might encompass design documents, user manuals, API documentation, among other resources. Concurrently, you amass all the source code associated with the software system.

Having compiled the necessary resources, you engage Corpusaige's CLI tool in batch command mode to index the gathered documents and source code. In this stage, the text data undergoes transformation into vector representations, translatable by the LLM. These vectors are then archived in a database, which could reside locally for debug-oriented purposes or in a cloud-based storage system for broader accessibility and scalability.

With the database now populated with vectorized data, you're ready to engage with the LLM. Deploying Corpusaige's CLI tool in REPL mode or through Corpusaige's plugin for Visual Studio Code, you can initiate ad-hoc dialogue sessions with the LLM regarding the software system. Whether your queries pertain to specific system components, require clarifications on intricate code sections, or seek advice on implementing novel features, the LLM is equipped to deliver insightful responses, fueled by the vector data, and based on a comprehensive understanding of the software system.

Your interaction with the system and the LLM doesn't end here. As you persist in your work on the software system, you continually enrich the vector database with new documents and modifications to the code, comments and meta-data related with the project as well as the very outcome of the AI's analysis itself. This ongoing data enrichment ensures the LLM's understanding remains current and precise and increases in scope and precision, enabling it to provide accurate and pertinent responses during the whole life cycle. 

In leveraging Corpusaige, you're no longer confronting an opaque software system. Instead, you've found a way to pierce the obscurity, gaining a clear understanding that simplifies system maintenance and enhancement over time.

## Installation

Installing the CLI tool:

```bash
pip install Corpusaige
```
The Visual Studio Code plugin can be found under the name __Corpusaige__

## Usage
```bash
python -m corpusaige --help
#or
crpsg --help

usage: crpsg [-h] {new,add,cli} ...

Corpusaige command line interface

positional arguments:
  {new,add,cli}
    new          Create a new corpus
    add          Add files to a corpus
    cli          Display the Corpusaige CLI 

options:
  -h, --help     show this help message and exit

```

## Used as a library

```python
import Corpusaige
# code examples
```

## Dependencies
### Langchain
Langchain is chosen as our main framework for Corpusaige because of its robustness in natural language processing and its compatibility with various language model APIs, aligning with our requirements.

### OpenAI Models
We leverage OpenAI's advanced language models, such as GPT-4, GPT-3.5 and Codex, for their superior language understanding and generation capabilities.

For our initial release, these technologies form the core. However, we recognize the dynamic nature of AI and are open to integrating other emerging models in future versions of Corpusaige, ensuring the tool remains relevant and effective.

### ChromaDb
ChromaDb is integrated for its efficient vector data storage capabilities, crucial in handling the high-dimensional vector representations of our processed documents. It aids in both local and cloud-based data storage, providing scalability and facilitating smooth interaction with the AI models.

## Configuration
Detailed configuration instructions go here.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Copyright and license

Copyright © 2023 Iwan van der Kleijn

Licensed under the MIT License 
[MIT](https://choosealicense.com/licenses/mit/)




