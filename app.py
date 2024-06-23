from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import threading
import uvicorn

# Configure the GenAI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load models
image_model = genai.GenerativeModel("gemini-pro-vision")
text_model = genai.GenerativeModel("gemini-pro")  # Replace "gemini-pro" with the appropriate text model name

# Set page config at the beginning
st.set_page_config(page_title="Blog & Image Description Generator", page_icon="✨", layout="wide")

# Create FastAPI app
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def get_gemini_response(input_text=None, image=None):
    if image is not None:
        response = image_model.generate_content(image)
    elif input_text:
        response = text_model.generate_content(input_text)
    else:
        response = None
    return response

@app.post("/store-rating")
async def store_rating(request: Request):
    data = await request.json()
    rating = data.get("rating")
    if rating is not None:
        st.session_state['ratings'].append(rating)
        return JSONResponse(content={"message": f"Thank you for your rating of {rating} stars!"})
    else:
        return JSONResponse(content={"message": "Rating not provided."}, status_code=400)

# Register FastAPI app with Streamlit
def run_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    server.run()

thread = threading.Thread(target=run_fastapi)
thread.start()

components.html("""
    <script>
        function showSpinner() {
            var spinner = document.getElementById('spinner');
            spinner.style.display = 'block';
        }
    </script>
""", height=0)

# Custom CSS for styling and animations
st.markdown("""
    <style>
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        @keyframes pulse {
            0% {transform: scale(1);}
            50% {transform: scale(1.05);}
            100% {transform: scale(1);}
        }
        @keyframes slideIn {
            from {transform: translateY(-100px); opacity: 0;}
            to {transform: translateY(0); opacity: 1;}
        }
        .title {
            font-family: 'Arial Black', Gadget, sans-serif;
            color: #4CAF50;
            animation: slideIn 1.5s ease-in-out, pulse 2s infinite;
        }
        .subtitle {
            font-family: 'Comic Sans MS', cursive, sans-serif;
            color: #2196F3;
            animation: pulse 2s infinite;
        }
        .instructions {
            font-family: 'Arial', sans-serif;
            color: #ff5722;
        }
        .btn-primary {
            background-color: #ff9800;
            color: white;
            font-size: 18px;
            border-radius: 8px;
            padding: 10px 24px;
            transition: background-color 0.3s ease;
        }
        .btn-primary:hover {
            background-color: #e68a00;
        }
        .generated-content {
            font-family: 'Georgia', serif;
            color: #000000;
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 8px;
            animation: fadeIn 1s ease-in-out;
        }
        .spinner {
            display: none;
            width: 50px;
            height: 50px;
            border: 8px solid #f3f3f3;
            border-top: 8px solid #3498db;
            border-radius: 50%;
            animation: spin 2s linear infinite;
            margin: auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        body {
            background-color: #1a1a1a !important;
            overflow: hidden;
        }
        .sparkles {
            pointer-events: none;
            position: fixed;
            width: 100%;
            height: 100%;
            background: url('https://media.giphy.com/media/K4lXxEcvqPMRa/giphy.gif') repeat center center fixed;
            z-index: -1;
            animation: sparkles 20s linear infinite;
        }
        @keyframes sparkles {
            0% { transform: translateY(0); }
            100% { transform: translateY(-2000px); }
        }
        input[type="text"], textarea {
            font-family: 'Arial', sans-serif;
            animation: fadeIn 1s ease-in-out;
        }
        input[type="text"]:focus, textarea:focus {
            border-color: #ff9800;
            box-shadow: 0 0 0 0.2rem rgba(255, 152, 0, 0.5);
        }
    </style>
""", unsafe_allow_html=True)

# Animated sparkles background
st.markdown('<div class="sparkles"></div>', unsafe_allow_html=True)

st.markdown('<h1 class="title">✨ Blog & Image Description Generator</h1>', unsafe_allow_html=True)
st.markdown("""
    <div class="subtitle">Welcome to the Blog & Image Description Generator!</div>
    <p>This tool helps you generate engaging blog content or image descriptions using the power of AI.</p>
    <p>You can either upload an image to get a description or enter text to generate a blog post.</p>
    """, unsafe_allow_html=True)

st.sidebar.header("Instructions")
st.sidebar.markdown("""
    <div class="instructions">
        <ol>
            <li><strong>Upload an Image:</strong> Click 'Browse files' to upload an image file.</li>
            <li><strong>Enter Text:</strong> Type or paste your text into the text area for blog post generation.</li>
            <li><strong>Generate Content:</strong> Click 'Generate Content' to see the magic!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload an image for description generation", type=["jpg", "jpeg", "png"])
image = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True, channels="RGB")

input_text = st.text_area("Enter text for blog post generation", height=200, placeholder="Type your blog content here...")

st.markdown("### Generate Content")

col1, col2 = st.columns([1, 3])
with col1:
    submit = st.button("Generate Content", type="primary")
with col2:
    st.write("Click the button to generate content based on the provided text or image.")

# Add animation for loading
components.html("""
    <script>
    function showSpinner() {
        var spinner = document.getElementById('spinner');
        spinner.style.display = 'block';
    }
    </script>
    <div id="spinner" class="spinner"></div>
    """, height=70)

# If submit button is clicked
if submit:
    st.markdown("<script>showSpinner();</script>", unsafe_allow_html=True)
    with st.spinner("Generating content..."):
        response = get_gemini_response(input_text=input_text, image=image)
        if response:
            st.success("Content generated successfully!")
            generated_content = response.text
            st.markdown(f"""
                <div class="generated-content">
                    <h3>Generated Content</h3>
                    <p id="generated-text">{generated_content}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Please provide either text or an image for generating content.")

st.sidebar.markdown("---")
st.sidebar.markdown("Developed by [Your Name](https://yourwebsite.com)")
st.sidebar.markdown("Powered by [Google Generative AI](https://ai.google/)")
