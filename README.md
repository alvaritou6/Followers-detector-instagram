# Instagram Network Auditor

A specialized Python tool designed to audit your social graph. It analyzes your Instagram data export to identify leveraging points (Fans) and deficits (Non-followers) without using the Instagram API or risking account bans.

## 🚀 Features

* **Safe & Local:** Runs entirely on your machine using your own data export. No login credentials required.
* **Smart Parsing:** Uses a recursive algorithm to handle Instagram's inconsistent JSON structures (works with both old and new data formats).
* **Dual Metrics:** Generates two distinct lists:
    * **Not Following Back:** Accounts you invest attention in with zero return.
    * **Fans:** Accounts investing attention in you that you haven't reciprocated.

## 📋 Prerequisites

* Python 3.x installed on your system.
* Your Instagram data export (JSON format).

## 📥 How to Get Your Data

1.  Open Instagram and go to **Settings** > **Your activity**.
2.  Select **Download your information**.
3.  Choose **"Some of your information"** and select **Followers and following**.
4.  **Crucial:** Select **JSON** as the format (not HTML).
5.  Once the download is ready, extract the zip file. You need two specific files:
    * `followers_1.json`
    * `following.json`

## 🛠️ Usage

1.  Place the script (`analysis.py`) in the same folder as your `.json` files.
2.  Run the script via terminal:

```bash
python analysis.py
