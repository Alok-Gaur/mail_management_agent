from typing import List, Dict, Optional
import requests
import json
import os
from env_secrets import config
import chromadb


class MailAgent:
    def __init__(self, db_session, chroma_client, user_id:int, agent_url:str = config.AGENT_URL, agent_model:str = config.AGENT_MODEL):
        self.db_session = db_session
        self.user_id = user_id
        self.agent_url = agent_url
        self.agent_model = agent_model
        self.chroma_client = chroma_client
    

    def _agent_generate(self, prompt:str, mat_tokens:int = 512, temperature:float = 0.0) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.agent_model,
            "prompt": prompt,
            "max_tokens": mat_tokens,
            "temperature": temperature,
        }
        response = requests.post(self.agent_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            return result.get("text", "").strip()
        else:
            raise Exception(f"Agent API request failed with status code {response.status_code}: {response.text}")
    

    # ---------------------
    # Classification
    # ---------------------
    def classify_email(self, subject: str, body: str, user_labels: List[str]) -> Dict:
        """
        Classify the email into one of user_labels.
        Returns dict: { "label": <label>, "confidence": <float>, "reason": <str> }
        """
        prompt = (
            "You are a classifier. Given an email SUBJECT and BODY, choose the best label\n"
            f"from the user-provided labels: {user_labels}\n\n"
            "Output a JSON object with keys: label, confidence (0-1), reason.\n\n"
            f"SUBJECT:\n{subject}\n\nBODY:\n{body}\n\n"
            "Respond ONLY with JSON."
        )
        raw = self._agent_generate(prompt, max_tokens=256)
        # Try to parse JSON robustly
        try:
            parsed = json.loads(raw)
        except Exception:
            # fallback simple parsing: try to find label word
            parsed = {"label": user_labels[0] if user_labels else "uncategorized",
                      "confidence": 0.0,
                      "reason": raw[:300]}
        return parsed
    

    # ---------------------
    # Chroma storage
    # ---------------------
    def _get_chroma(self):
        if chromadb is None:
            raise RuntimeError("chromadb not available; pip install chromadb")
        if self._chroma_client is None:
            self._chroma_client = chromadb.Client()
        return self._chroma_client

    def store_to_chromadb(self, email_id: str, subject: str, body: str, metadata: dict):
        client = self._get_chroma()
        # collection name per user
        col_name = f"user_{self.user_id}_emails"
        collection = client.get_or_create_collection(col_name)
        doc = f"Subject: {subject}\n\n{body}"
        collection.add(
            documents=[doc],
            metadatas=[metadata],
            ids=[email_id]
        )
    

    # ---------------------
    # Finance management
    # ---------------------
    def manage_finance(self, subject: str, body: str, label: str) -> Optional[dict]:
        """
        If label indicates expense/income, extract structured details and store to relational DB.
        Returns stored record data (dict) or None.
        """
        if label.lower() not in ("expense", "income"):
            return None

        prompt = (
            "Extract a JSON object with keys: type (expense|income), amount (number), currency, "
            "date (YYYY-MM-DD or best guess), vendor, category, notes.\n\n"
            "EMAIL SUBJECT:\n"
            f"{subject}\n\nEMAIL BODY:\n{body}\n\nRespond only with JSON."
        )
        raw = self._agent_generate(prompt, max_tokens=200)
        try:
            data = json.loads(raw)
        except Exception:
            # minimal fallback
            data = {"type": label, "amount": None, "currency": None, "date": None, "vendor": None, "category": None, "notes": raw[:300]}

        # Example: persist to DB (adjust model and fields to your schema)
        try:
            # finance = FinanceEntry(
            #     user_id=self.user_id,
            #     type=data.get("type"),
            #     amount=data.get("amount"),
            #     currency=data.get("currency"),
            #     date=data.get("date"),
            #     vendor=data.get("vendor"),
            #     category=data.get("category"),
            #     notes=data.get("notes")
            # )
            # self.db.add(finance)
            # self.db.commit()
            # return {"id": finance.id, **data}
            return data  # placeholder: replace with actual DB save
        except Exception as e:
            # self.db.rollback()
            raise

    # ---------------------
    # Response generation
    # ---------------------
    def generate_response(self, subject: str, body: str, user_role: str, label: str, tone: str = "polite") -> Optional[str]:
        """
        If email requires response (based on label + role), generate reply text.
        user_role: e.g., "owner", "student", "recruiter", "customer_service"
        """
        # Simple heuristic: generate reply for "customer query" or when label indicates response needed
        should_reply = label.lower() in ("customer query", "inquiry", "question") or user_role.lower() in ("owner", "student")
        if not should_reply:
            return None

        prompt = (
            f"You are an assistant. Compose a {tone} email reply tailored to a {user_role}.\n"
            "Include greeting, concise body addressing the customer's points, and a polite closing.\n\n"
            "ORIGINAL SUBJECT:\n" + subject + "\n\nORIGINAL BODY:\n" + body + "\n\nRespond only with the email body text (no JSON)."
        )
        reply = self._agent_generate(prompt, max_tokens=400)
        return reply.strip()

    # ---------------------
    # Calendar scheduling
    # ---------------------
    def schedule_event(self, subject: str, body: str, label: str) -> Optional[dict]:
        """
        If the content contains an event, extract event info + priority/usability and persist.
        Returns event dict or None.
        """
        prompt = (
            "Extract event information (if any) from the email. Output JSON with keys: "
            "title, start (ISO or best guess), end (ISO or best guess or null), location, "
            "description, priority (low|medium|high), usability (0-1) . If no event, return {\"event\": null}.\n\n"
            f"SUBJECT:\n{subject}\n\nBODY:\n{body}\n\nRespond only with JSON."
        )
        raw = self._agent_generate(prompt, max_tokens=200)
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"event": None}

        event = parsed.get("event") or parsed
        if not event or event.get("title") is None:
            return None

        # Persist to DB / calendar (placeholder)
        try:
            # calendar = CalendarEvent(
            #     user_id=self.user_id,
            #     title=event["title"],
            #     start=event.get("start"),
            #     end=event.get("end"),
            #     location=event.get("location"),
            #     description=event.get("description"),
            #     priority=event.get("priority"),
            #     usability=event.get("usability")
            # )
            # self.db.add(calendar)
            # self.db.commit()
            # return {"id": calendar.id, **event}
            return event  # placeholder
        except Exception:
            # self.db.rollback()
            raise

    # ---------------------
    # Orchestration
    # ---------------------
    def run(self, email_id: str, subject: str, body: str, user_labels: List[str], user_role: str) -> Dict:
        """
        Full pipeline: classify, store, finance, response, schedule.
        Returns a summary dict with actions taken.
        """
        summary = {"email_id": email_id}

        classification = self.classify_email(subject, body, user_labels)
        label = classification.get("label")
        summary["classification"] = classification

        # store raw email + metadata in chroma
        metadata = {"user_id": self.user_id, "label": label, "classification_reason": classification.get("reason")}
        try:
            self.store_to_chromadb(email_id, subject, body, metadata)
            summary["stored_chroma"] = True
        except Exception as e:
            summary["stored_chroma"] = False
            summary["chroma_error"] = str(e)

        # finance
        try:
            fin = self.manage_finance(subject, body, label)
            summary["finance"] = fin
        except Exception as e:
            summary["finance_error"] = str(e)

        # response
        try:
            reply = self.generate_response(subject, body, user_role, label)
            summary["reply"] = reply
        except Exception as e:
            summary["reply_error"] = str(e)

        # schedule
        try:
            event = self.schedule_event(subject, body, label)
            summary["event"] = event
        except Exception as e:
            summary["event_error"] = str(e)

        return summary
