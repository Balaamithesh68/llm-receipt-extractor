import json
import urllib.request
import streamlit as st

# Page setup
st.set_page_config(page_title="AI Cashier", page_icon="🛒", layout="centered")


def call_ollama(prompt_text: str) -> dict:
    url = "http://localhost:11434/api/generate"
    payload = {"model": "ai-cashier", "prompt": prompt_text, "stream": False}

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            return json.loads(res["response"])
    except Exception as e:
        return {"error": str(e)}


# --- UI LAYOUT ---
st.title("🛒 Offline AI Cashier")
st.caption("Powered by local Qwen 2.5 (1.5B) + Custom LoRA")

receipt_input = st.text_area(
    "Drop raw, messy receipt dump here:",
    value="went to cvs got a 12pk of redbull for 21.50, two snickers bars 1.50 ea and some advil 9.00. total was 33.50",
    height=120,
)

if st.button("⚡ Process Receipt", type="primary"):
    if not receipt_input.strip():
        st.warning("Paste some text first!")
    else:
        with st.spinner("RTX 3050 is parsing the chaos..."):
            data = call_ollama(receipt_input)

        if "error" in data:
            st.error(f"Backend Error: {data['error']}")
        else:
            store_name = data.get("store", "Unknown")
            raw_items = data.get("items", [])

            # --- THE PYTHON MATH INTERCEPTOR ---
            # We let the AI catch the total sticker price, but force Python to calculate Unit Price.
            items = []
            for item in raw_items:
                sticker_price = item.get("total_price", item.get("price", 0.0))
                qty = item.get("qty", item.get("quantity", 1))

                try:
                    c_price = float(str(sticker_price).replace("$", "").strip())
                    c_qty = int(qty)

                    if c_qty > 0:
                        item["price"] = round(c_price / c_qty, 2)
                    else:
                        item["price"] = c_price
                except (ValueError, TypeError, ZeroDivisionError):
                    item["price"] = sticker_price

                items.append(item)
            # -----------------------------------

            st.subheader(f"🏪 Store: **{store_name}**")

            if items:
                st.table(items)

                # --- THE FUZZY CSV EXPORTER ---
                import csv
                import io

                cleaned_rows = []
                for row in items:
                    cleaned = {
                        "name": row.get("name", row.get("item", row.get("desc", ""))),
                        "qty": row.get("qty", row.get("quantity", row.get("count", ""))),
                        "unit": row.get("unit", row.get("measure", row.get("type", ""))),
                        "price": row.get("price", row.get("unit_price", row.get("cost", "")))
                    }
                    cleaned_rows.append(cleaned)

                buffer = io.StringIO()
                writer = csv.DictWriter(buffer, fieldnames=["name", "qty", "unit", "price"])
                writer.writeheader()
                writer.writerows(cleaned_rows)

                st.download_button(
                    label="📥 Download as Spreadsheet (.CSV)",
                    data=buffer.getvalue(),
                    file_name=f"{store_name.lower()}_receipt.csv",
                    mime="text/csv",
                    type="secondary"
                )

            with st.expander("👀 Inspect Raw JSON Payload"):
                st.json(data)