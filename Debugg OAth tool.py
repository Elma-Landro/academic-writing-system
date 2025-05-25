import streamlit as st
import os

st.title("🔍 OAuth Debug Helper")

st.write("Let's check your OAuth setup step by step!")

# Check 1: Streamlit Secrets
st.header("1. Checking Streamlit Secrets")
try:
    if hasattr(st, 'secrets') and 'google_oauth' in st.secrets:
        st.success("✅ google_oauth section found in secrets!")
        
        # Check each required field
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri', 'redirect_uris']
        for field in required_fields:
            if field in st.secrets['google_oauth']:
                # Hide sensitive info
                value = st.secrets['google_oauth'][field]
                if 'secret' in field.lower():
                    display_value = f"{value[:10]}..." if len(value) > 10 else "***"
                else:
                    display_value = value
                st.write(f"   ✅ {field}: {display_value}")
            else:
                st.error(f"   ❌ Missing: {field}")
    else:
        st.error("❌ No google_oauth section found in secrets!")
        st.write("You need to add secrets in your Streamlit Cloud dashboard.")
        
except Exception as e:
    st.error(f"❌ Error checking secrets: {e}")

# Check 2: Current URL
st.header("2. Checking Current App URL")
query_params = st.query_params
st.write("Query parameters:", query_params)

# Check 3: Session State
st.header("3. Checking Session State")
st.write("Current session state keys:")
for key in st.session_state.keys():
    st.write(f"   - {key}")

# Check 4: Environment Info
st.header("4. Environment Info")
st.write(f"Python version: {os.sys.version}")
st.write("Installed packages (OAuth related):")
try:
    import streamlit_oauth
    st.write("   ✅ streamlit-oauth: installed")
except ImportError:
    st.error("   ❌ streamlit-oauth not installed")

try:
    import google.auth
    st.write("   ✅ google-auth available")
except ImportError:
    st.error("   ❌ google-auth not available")

# Simple test button
st.header("5. Test Basic OAuth Flow")
if st.button("Test OAuth Setup"):
    try:
        from streamlit_oauth import OAuth2Component
        
        # Try to create OAuth component
        oauth2 = OAuth2Component(
            st.secrets["google_oauth"]["client_id"],
            st.secrets["google_oauth"]["client_secret"],
            st.secrets["google_oauth"]["auth_uri"],
            st.secrets["google_oauth"]["token_uri"],
            st.secrets["google_oauth"].get("redirect_uris", ""),
        )
        st.success("✅ OAuth component created successfully!")
        
    except Exception as e:
        st.error(f"❌ Error creating OAuth component: {e}")

st.divider()
st.write("**Next Steps:**")
st.write("1. If secrets are missing, we'll set them up")
st.write("2. If redirect URI is wrong, we'll fix it") 
st.write("3. If Google setup is wrong, we'll configure it")
