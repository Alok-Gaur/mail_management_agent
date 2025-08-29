# Mail Managment Agent

---
## Introduction
It is a single agent that monitors your inbox, classifies incoming mail into categories (expense, income, customer query, event, recruiter), and then takes autonomous actions:
- Logs expenses/income to your database
- Crafts and sends personalized replies to customers
- Schedules important events in your calendar
- Researches recruiter emails, drafts tailored responses, and notifies you

---
## Tech Stack
- Python
- Redis (manage mail queue)
- Mongodb
- FastAPI (for server)
- ollama (for agent)
- google cloud

---
## Steps to follow
It is rough steps which are needed to follow for completion of this project by the estimation on date 30-08-2025.
Required steps:
- start google cloud pub/sub (publisher/subscriber)
- create FastAPI server to get the older mails and new notifications by google pub/sub.
- create a Radis Queue to manage mails
- create Classification module
- create different module for different actions(like manage finances, schedule event, personalized mail etc.)

---
**Author**: [Alok Gaur](https://github.com/Alok-Gaur)
