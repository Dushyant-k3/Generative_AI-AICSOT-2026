Week 2 Summary:

1. SETUP: I first created and activated virtual environment and then installed various dependencies like openai,      python-dotenv, requests, textual. Then I added my key file (.env) to .gitignore.

2. build1 : i have learned how to read and write a file safely in my COL cources, so I implemented that easily. Then I learnt the regular expression (regex) to hunt for the secret XML tags. I understand the syntax of re.search(pattern, text)  and then put the results back into the chat using <tool_response> tags.

3. build2: here, I learned about the built-in parsing tools. we gave the OpenAI API a strict JSON Schema(TOOLS), where the SDK handles the formatting automatically. I understood the use of 'json.loads()' to turn the AI's raw text into Python dictionaries and 'json.dumps()' to turn your Python results back into text. Also, learnt the key difference betwen the json.load and json.loads, one for giving the data to the users computer for reading and writing data to physical files and one for returning the string. I also learned json.dumps (which is used to translating strings and dictionaries into the computer's memory).

4. build3: This was one of the satisfying part to the chatBot window working beautifully. Here, first recall about the CSS(I have done CSS for web pages) and how the chatBOT window was designed using that. Here, the use of "textual" python library to collab with the CSS to built the Terminal User Interface(TUI). 
After that, I noted in my notes the concept of Asynchronous Programming, where calculations happen at the back without affecting the user experience, like delay while getting the answer, slow response or error, the user can still type (run_worker(thread=True) and call_from_thread()).

5. Final Project (Web and True MCP): Here, I combined the loop from build2 and the TUI from build3 into my final agent.py file. I also added live real-world tools! I used the Serper API for "search_web" and trafilatura for "read_page". For the AlphaXiv MCP server requirement, I actually integrated the real Model Context Protocol. I installed the official mcp python library and used asyncio to bridge my synchronous TUI code with the asynchronous MCP client. My code now uses npx to launch the external alphaxiv server in the background, so the bot can truly search and read real academic papers using discover_papers and get_paper_content.

