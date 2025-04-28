import streamlit as st
import wikipedia
import google.generativeai as genai
import urllib.parse

def Answer(x):
    try:
        genai.configure(api_key="AIzaSyDpEGGhkNIWIQfdBk18jJzW6QfsZyy27nE")
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        response = model.generate_content(x)
        if response and hasattr(response, 'parts') and response.parts:
            return response.parts[0].text
        else:
            return "❗ No valid response."
    except Exception as e:
        return f"❗ Error: {str(e)}"

def get_maps_link(place, city):
    query = urllib.parse.quote(f"{place} {city}")
    return f"https://www.google.com/maps/search/?api=1&query={query}"

def get_city_description(city):
    try:
        summary = wikipedia.summary(city, sentences=3, auto_suggest=False)
        return summary
    except wikipedia.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], sentences=3, auto_suggest=False)
            return summary
        except:
            return "❗ Couldn't find a proper description for this city."
    except:
        return "❗ Couldn't find a proper description for this city."

def get_travel_info_gemini(city):
    prompt = f"""Provide structured travel details for {city} with the following sections:
    🏛 Famous Places
    - (List three famous places)
    🍽 Popular Foods
    - (List three popular local foods)
    🛍 Best Malls
    - (List three best shopping malls)
    🍴 Recommended Restaurants
    - (List three recommended restaurants)

    Each item should be on a new line with a '-' bullet point. Only provide names, no extra description."""
    try:
        response = Answer(prompt)
        return response if response else "❗ No valid response from Gemini AI."
    except Exception as e:
        return f"❗ Error fetching data from Gemini AI: {str(e)}"

st.title("🌍 AI Travel Guide")

city = st.text_input("Enter a city name:")

if city:
    st.markdown(
        f"<div class='section-header'>🌐 Explore {city.title()} on <a class='map-link' href='{get_maps_link(city, '')}' target='_blank'>Google Maps</a></div>",
        unsafe_allow_html=True
    )

    if st.button("Get Travel Information"):
        st.subheader(f"📍 About {city}")
        description = get_city_description(city)
        st.markdown(f"<div class='description'>{description}</div>", unsafe_allow_html=True)
        details = get_travel_info_gemini(city)
        st.text("Raw Response from Gemini AI:")
        st.code(details)

        if details and isinstance(details, str):
            sections = {
                "🏛 Famous Places": [],
                "🍽 Popular Foods": [],
                "🛍 Best Malls": [],
                "🍴 Recommended Restaurants": []
            }

            current_section = None
            for line in details.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if "🏛 Famous Places" in line:
                    current_section = "🏛 Famous Places"
                elif "🍽 Popular Foods" in line:
                    current_section = "🍽 Popular Foods"
                elif "🛍 Best Malls" in line:
                    current_section = "🛍 Best Malls"
                elif "🍴 Recommended Restaurants" in line:
                    current_section = "🍴 Recommended Restaurants"
                elif current_section:
                    sections[current_section].append(line.strip('-• ').strip())

            for title, items in sections.items():
                st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
                if items:
                    for item in items:
                        link = get_maps_link(item, city)
                        st.markdown(
                            f"<div class='item'>🔹 <b>{item}</b> | <a class='map-link' href='{link}' target='_blank'>Open in Google Maps</a></div>",
                            unsafe_allow_html=True)
                else:
                    st.markdown("<div class='item'>🔹 <i>N/A</i></div>", unsafe_allow_html=True)
        else:
            st.error("❗ No valid data received from Gemini AI.")
else:
    st.warning("⚠ Please enter a city name.")
