# Django DocuSign eSignature Integration

This Django application allows users to create contracts, send them to signers via email, and sign contracts using the **DocuSign eSignature REST API**. Users must register and log in to use the contract creation and signing features.

## Features
- **User Authentication**: Users must register and log in to create and manage contracts.
- **Contract Creation**: Users can create contracts with dynamic content, including signer details, contract body, and dates.
- **DocuSign Integration**: Contracts are sent to signers via email using the DocuSign eSignature REST API.
- **Embedded Signing**: Signers can sign contracts directly within the application using DocuSign's embedded signing feature.
- **Database Storage**: Contract details are stored in the database for future reference.

---

## Prerequisites

Before running this project, ensure you have the following:

1. **Python 3.8+**: Install Python from [python.org](https://www.python.org/).
2. **Django 4.0+**: Install Django using `pip install django`.
3. **DocuSign Developer Account**: Sign up for a free developer account at [DocuSign Developer Center](https://developers.docusign.com/).
4. **DocuSign Integration Key**: Create an integration key (client ID) in your DocuSign developer account.
5. **DocuSign Redirect URI**: Set up a redirect URI in your DocuSign developer account (e.g., `http://localhost:8000/docusign/callback/`).
6. **wkhtmltopdf**: Install `wkhtmltopdf` for converting HTML to PDF. Download it from [wkhtmltopdf.org](https://wkhtmltopdf.org/).

---

## Installation

Follow these steps to set up the project on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/basetbehzad/django_docusign_esignature.git
cd django_docusign_esignature
```
### 2. Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Set Up Environment Variables
Create a .env file in the root directory and add the following variables:
```plaintext
DOCUSIGN_CLIENT_ID=your-docusign-client-id
DOCUSIGN_CLIENT_SECRET=your-docusign-client-secret
DOCUSIGN_REDIRECT_URI=http://localhost:8000/docusign/callback/
DOCUSIGN_ACCOUNT_ID=your-docusign-account-id
DOCUSIGN_API_BASE_URL=https://demo.docusign.net/restapi
SECRET_KEY=your-django-secret-key
DEBUG=True
```
### 5. Apply Migrations
```bash
python manage.py migrate
```
### 6. Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```
### 7. Run the Development Server
```bash
python manage.py runserver
```
Visit http://localhost:8000 in your browser to access the application.

---

## Usage
### 1. Register and Log In
Visit the registration page (/register/) to create a new account.
Log in using your credentials at /login/.
### 2. login to docusign and get access token
go to (docusign/login) url
### 3. Create a Contract

Navigate to the contract creation page (/create-contract/).
Fill in the form with the following details:

- **Signer's Name**: Name of the primary signer.
- **Signer's Email**: Email of the primary signer.
- **CC's Name**: Name of the contract recipient.
- **CC's Email**: Email of the contract recipient.
- **Contract Body**: The content of the contracts
- **Contract Date**: The date of the contract.
Click Submit to send the contract to the signer via email.
### 4. Sign the Contract
The signer will receive an email with a link to sign the contract.
The signing process uses DocuSign's embedded signing feature, allowing the signer to sign the contract directly within the application.
### 5. View Contracts
Logged-in users can view their contracts on the dashboard (/dashboard/).

# DocuSign API Integration

- **OAuth2 Authentication**: Users authenticate with DocuSign to obtain an access token.
- **Envelope Creation**: Contracts are created as DocuSign envelopes and sent to signers.
- **Embedded Signing**: Signers can sign contracts directly within the application.

## Key API Endpoints Used
- **Authorization**: /oauth/auth (OAuth2 authorization)
- **Token Exchange**: /oauth/token (OAuth2 token exchange)
- **Envelope Creation**: /restapi/v2.1/accounts/{accountId}/envelopes (Create and send envelopes)
- **Embedded Signing**: /restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}/views/recipient (Generate signing URLs)

---

## Contact

If you have any questions or need assistance, feel free to reach out:

baset behzad: basetbehzad2017@gmail.com
GitHub: https://github.com/basetbehzad
