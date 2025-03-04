# Text-to-SQL

![image](https://www.jetadmin.io/blog/content/images/2023/03/Frame-315.svg)

## Overview

This project leverages the **Gemini API** to automatically convert natural language queries into SQL queries. It allows users with no SQL knowledge to easily interact with databases by simply typing out questions in plain language. For example, a user can ask:  
**"Zəhmət olmasa, profiti ən yüksək olan top 5 customer-i mənə göstər və profitini yaz"**  
and the system will automatically translate this into a corresponding SQL query to retrieve the results.

## Features

- **Natural Language Processing (NLP)**: Uses Gemini API to process user input and generate valid SQL queries.
- **User-Friendly Interface**: Non-technical users can query databases without needing to know SQL.
- **Customizable**: The system can be adapted to work with any SQL-based database, given the right structure.

## Challenges

While the system provides a simple interface for interacting with databases, there are some challenges to consider:

1. **Database Size**:  
   If the database is large, the learning process can become slower, and SQL query generation might face performance issues.

2. **Ambiguity in Queries**:  
   User queries are sometimes vague or too general, which can make it difficult to generate accurate SQL queries and lead to potential errors in results.

3. **Security Risks**:  
   Incorrectly used automatic SQL generation can open up vulnerabilities such as **SQL Injection**, which could compromise the database's security. Proper precautions are needed to mitigate these risks.
