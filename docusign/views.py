
import uuid
from datetime import timedelta
import pdfkit
import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import Contract, TokenStorage, User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import base64
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, Tabs, SignHere, \
    RecipientViewRequest, Recipients
from docusign_esign import ApiException


def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not User.objects.filter(username=name).exists():
            user = User.objects.create_user(username=name, email=email, password=password)
            user.save()
            return JsonResponse({"message": "Registration successful"}, status=200)
        else:
            return JsonResponse({"error": "User already exists"}, status=400)
    return render(request, "register.html")


def login_user(request):
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")
        user = authenticate(username=name, password=password)
        if user:
            login(request, user)  # Log the user in
            request.session["user_id"] = user.id  # Store user_id in session
            print(f"User ID stored in session: {user.id}")  # Debugging
            return redirect("dashboard")
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)
    return render(request, "login.html")


def logout_user(request):
    logout(request)
    return redirect("login")


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    contracts = Contract.objects.filter(user=request.user)
    return render(request, "dashboard.html", {"contracts": contracts})


def docusign_login(request):
    """Initiates the login process by redirecting to DocuSign's authorization URL."""

    auth_url = (
        f"{settings.DOCUSIGN_AUTH_SERVER}/oauth/auth?"
        f"response_type=code&"
        f"client_id={settings.DOCUSIGN_CLIENT_ID}&"
        f"redirect_uri={settings.DOCUSIGN_REDIRECT_URI}&"
        f"scope=signature&"
    )
    return redirect(auth_url)


def store_tokens_in_db(access_token, refresh_token, expires_in):
    """Store tokens in the database."""
    expiration_time = timezone.now() + timedelta(seconds=expires_in)
    TokenStorage.objects.update_or_create(
        id=1,
        defaults={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expiration_time,
        }
    )


def docusign_callback(request):
    """Handles the OAuth2 callback, exchanges authorization code for access token."""
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Authorization failed: No code provided", status=400)

    # Exchange authorization code for an access token
    token_url = f"{settings.DOCUSIGN_AUTH_SERVER}/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.DOCUSIGN_REDIRECT_URI,
        "client_id": settings.DOCUSIGN_CLIENT_ID,
        "client_secret": settings.DS_CLIENT_SECRET,  # Include client secret for token exchange
    }

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        # logger.error(f"Token exchange failed: {e}")
        return HttpResponse(f"Error during token exchange: {str(e)}", status=500)

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in")

        store_tokens_in_db(access_token, refresh_token, expires_in)

        return redirect(reverse('dashboard'))
    else:
        return HttpResponse(f"Error during token exchange: {response.text}", status=response.status_code)


def refresh_access_token():
    """Refresh the access token using the refresh token."""
    try:
        token_data = TokenStorage.objects.get(id=1)  # Retrieve tokens from the database
    except TokenStorage.DoesNotExist:
        raise Exception("No tokens found. Please reauthorize the app.")

    if timezone.now() >= token_data.expires_at:
        # Token has expired, refresh it
        refresh_url = f"{settings.DOCUSIGN_AUTH_SERVER}/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token_data.refresh_token,
            "client_id": settings.DOCUSIGN_CLIENT_ID,
            "client_secret": settings.DOCUSIGN_CLIENT_SECRET,
        }

        response = requests.post(refresh_url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            expires_in = tokens.get("expires_in")

            # Update tokens in the database
            store_tokens_in_db(access_token, refresh_token, expires_in)
        else:
            raise Exception(f"Failed to refresh token: {response.text}")
    else:
        access_token = token_data.access_token

    return access_token


@login_required
def create_envelope(request):
    if request.method == 'POST':
        # Input data from the request
        signer_name = request.POST.get("signer_name")
        signer_email = request.POST.get("signer_email")
        cc_name = request.POST.get("cc_name")
        cc_email = request.POST.get("cc_email")
        contract_body = request.POST.get("contract_body")
        contract_date = request.POST.get("contract_date")
        account_id = settings.DOCUSIGN_ACCOUNT_ID
        access_token = refresh_access_token()

        print(f"Access token retrieved: {access_token}")
        print(f"Signer Name: {signer_name}")
        print(f"Signer Email: {signer_email}")
        print(f"CC Name: {cc_name}")
        print(f"CC Email: {cc_email}")
        print(f"account id: {account_id}")

        # Validate input
        if not signer_name or not signer_email:
            return HttpResponse("Error: Signer details are required.", status=400)

        if not access_token:
            return HttpResponse("Error: Access token not found", status=401)

        client_user_id = str(uuid.uuid4())  # Generate a unique client_user_id
        # Create the envelope request object
        envelope_definition = make_envelope(
            signer_name=signer_name,
            signer_email=signer_email,
            cc_name=cc_name,
            cc_email=cc_email,
            client_user_id=client_user_id,
            contract_body=contract_body,
            contract_date=contract_date
        )

        api_client = ApiClient()
        api_client.host = settings.DOCUSIGN_API_BASE_URL
        api_client.set_default_header("Authorization", f"Bearer {access_token}")

        try:
            # Call Envelopes::create API method
            envelopes_api = EnvelopesApi(api_client)
            results = envelopes_api.create_envelope(account_id=account_id, envelope_definition=envelope_definition)

            envelope_id = results.envelope_id
            print(f"Envelope Created: ID = {envelope_id}")

            contract = Contract.objects.create(
                user=request.user,  # Link contract to logged-in user
                signer_name=signer_name,
                signer_email=signer_email,
                status="sent",  # Initial status when contract is sent
                contract_content=contract_body,
                envelope_id=envelope_id  # Store DocuSign Envelope ID
            )
            contract.save()

            return redirect_to_signing_ceremony(api_client, account_id, envelope_id, client_user_id, signer_name,
                                                signer_email)

        except ApiException as e:
            print("API Exception Details:")
            print(f"Status Code: {e.status}")
            print(f"Reason: {e.reason}")
            print(f"Body: {e.body}")
            return HttpResponse(f"An error occurred: {e.body}", status=500)

    # Handle GET request to render the form
    elif request.method == 'GET':
        return render(request, 'create_contract.html')

    # Method not allowed
    return HttpResponse("Method not allowed", status=405)


def make_envelope(signer_name, signer_email, cc_name, cc_email, client_user_id, contract_body, contract_date):
    html_document = f"""
        <!DOCTYPE html>
        <html>
            <body>
                <h1>Contract Agreement</h1>
                <p>{contract_body}</p>
                <p><strong>Full Name:</strong> {signer_name}</p>
                <p><strong>Email:</strong> {signer_email}</p>
                <p><strong>CC Name:</strong> {cc_name}</p>
                <p><strong>CC Email:</strong> {cc_email}</p>
                <p><strong>Date:</strong> {contract_date}</p>
                <p><strong>Signature(Signer 1):</strong></p>
                <p><strong>Signature(Signer 2):</strong></p>
            </body>
        </html>
        """
    print("HTML Document:")
    print(html_document)

    pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

    # Convert HTML to PDF
    pdf_path = "temp_contract.pdf"
    pdfkit.from_string(html_document, pdf_path, configuration=pdfkit_config)

    # Read the PDF file and encode it in base64
    with open(pdf_path, "rb") as pdf_file:
        doc1_b64 = base64.b64encode(pdf_file.read()).decode("ascii")

    # Create the Document model
    document1 = Document(
        document_base64=doc1_b64,
        name="Contract Agreement",
        file_extension="pdf",  # Use PDF instead of HTML
        document_id="1"
    )

    # Create the signer model
    signer1 = Signer(
        email=signer_email,
        name=signer_name,
        recipient_id="1",
        routing_order="1",
        client_user_id=client_user_id  # Unique identifier for embedded signing
    )

    sign_here1 = SignHere(
        anchor_string="Signature(Signer 1):",  # Use anchor text for dynamic positioning
        anchor_units="pixels",
        anchor_x_offset="20",
        anchor_y_offset="10"
    )
    signer_tabs = Tabs(sign_here_tabs=[sign_here1])
    signer1.tabs = signer_tabs

    # Create the CC model (Carbon Copy recipient)
    signer2 = Signer(
        email=cc_email,
        name=cc_name,
        recipient_id="2",
        routing_order="2"
    )

    sign_here2 = SignHere(
        anchor_string="Signature(Signer 2):",
        anchor_units="pixels",
        anchor_x_offset="20",
        anchor_y_offset="10"
    )
    signer2.tabs = Tabs(sign_here_tabs=[sign_here2])

    # Create the envelope recipients model
    recipients = Recipients(signers=[signer1, signer2])

    # Create EnvelopeDefinition
    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign the contract agreement",
        documents=[document1],
        recipients=recipients,
        status="sent",  # Automatically sends the envelope
    )
    return envelope_definition


def redirect_to_signing_ceremony(api_client, account_id, envelope_id, client_user_id, signer_name, signer_email):
    # Create the embedded signing view (RecipientViewRequest)
    view_request = RecipientViewRequest(
        authentication_method="email",
        client_user_id=client_user_id,  # Same as client_user_id in signer
        recipient_id="1",
        return_url="http://127.0.0.1:8000/sign_completed",  # Redirect here after signing
        user_name=signer_name,
        email=signer_email,
    )

    try:
        envelopes_api = EnvelopesApi(api_client)
        results = envelopes_api.create_recipient_view(account_id=account_id, envelope_id=envelope_id,
                                                      recipient_view_request=view_request)
        return redirect(results.url)  # Redirect the user to the signing ceremony

    except ApiException as e:
        print("API Exception Details:")
        print(f"Status Code: {e.status}")
        print(f"Reason: {e.reason}")
        print(f"Body: {e.body}")
        return HttpResponse(f"An error occurred: {e.body}", status=500)


def success(request):
    return render(request, "success.html")
