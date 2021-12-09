python -m spacy download en_core_web_sm
python -m nltk.downloader punkt
mkdir -p ~/.streamlit/
echo "[general]"  > ~/.streamlit/credentials.toml
echo "email = \"fabian_coll@bentley.edu\""  >> ~/.streamlit/credentials.toml
echo "[server]"  > ~/.streamlit/config.toml 
echo "headless = true"  >> ~/.streamlit/config.toml
echo "port = $PORT"  >> ~/.streamlit/config.toml
echo "enableCORS = true"  >> ~/.streamlit/config.toml