# 🧪 **Neuroscience Foundation Q&A Crew**

**IMPORTANT**: The code must be developed using **Python** and shared on **Github**.

## 📚 **Case Scenario**
You’ve been hired to prototype an intelligent assistant for a neuroscience foundation. This assistant should help researchers, students, and curious minds answer questions about dopamine, pulling from both **internal research papers** and **external trusted sources on the web**.
To accomplish this, you will design a multi-agent system ("the crew") powered by Large Language Models (LLMs). This crew should collaborate to **retrieve, analyze, and synthesize** information from 10 provided research papers PDFs and supplement answers with reliable web-based sources if needed. Importantly, your crew should be able to **remember** the conversation context to support follow-up questions.

## 🧠 **Objective:**
Create a multi-agent system capable of answering questions about **dopamine** by performing:

* **RAG** (Retrieval-Augmented Generation) using 10 PDF documents
* **Live web search** to fill in gaps or verify claims
* **Source-aware generation**: Each answer should clearly state where the information came from (e.g., “Paper X, page 5”, or “NIH.gov”)
* **Conversational memory**: Maintain useful dialogue context across a session

## 📦 **Resources Provided:**
* A set of 10 neuroscience-focused research PDFs about dopamine

## ✅ **What We Expect From You**
**Required Features:**
* 🧑‍🤝‍🧑 A **modular crew** of agents (e.g., Retriever, Synthesizer, WebSearcher, Memory Keeper)
* 🧾 Responses that include **source citations** (PDF metadata or web URLs)
* 🧠 A functioning **memory system** that allows contextual follow-up questions
* 🔄 A simple **interface** to interact with the crew

**Extra Points Bonus Features:**
* 🗺️ **Diagram + explanation** of your agent architecture
* 📊 Structured response output (e.g., JSON with answer, sources, and reasoning steps)
* 🕵️‍♂️ Handling ambiguous or controversial dopamine topics by flagging or explaining uncertainty
* 🧱 **Optional Deployment Architecture**:
	* A document describing how you'd deploy this crew
	* Include infrastructure considerations (memory, scalability, cost)

## 🧪 **Sample Questions You Might Want to Test**
*These don’t need to be hardcoded — just useful for your testing.*
* What is dopamine and what role does it play in motivation?
* How does dopamine influence learning and reward processing?
* Are dopamine detox strategies backed by science?
* How is dopamine involved in addiction vs habit formation?
* Can you summarize differences in dopamine function between ADHD and Parkinson's disease?

## 📁 **Expected Output**
**Github repo including:**
* **Readme** with **decisions made**, **instructions**, and/or any additional comments you wish to make
* **Code developed** to solve the Challenge

## **Good Luck!**