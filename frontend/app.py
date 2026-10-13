
import streamlit as st
import requests

from api_client import (
    register_user,
    login_user,
    get_profile,
    get_trips,
    get_destinations,
    create_trip,
    update_trip,
    delete_trip,
    ask_travel_question,
)

st.set_page_config(
    page_title="TravelWise AI",
    page_icon="✈️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #EDF5EA;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("✈️ TravelWise AI")
st.write("Plan your trips and get AI-powered travel guidance.")

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None



def show_error(error):
    """Display a friendly message without exposing technical details."""
    message = str(error)

    if isinstance(error, requests.Timeout):
        st.error(
            "The request took too long. Please try again later."
        )
    elif isinstance(error, requests.ConnectionError):
        st.error(
            "TravelWise cannot connect to the backend. "
            "Please check that the application is running."
        )
    elif isinstance(error, requests.RequestException):
        st.error(message)
    else:
        st.error(
            "Something went wrong. Please try again. "
            "If the problem continues, check the application logs."
        )


if not st.session_state.token:
    login_tab, register_tab = st.tabs(["Log in", "Create account"])

    with login_tab:
        st.subheader("Welcome back")
        with st.form("login_form"):
            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Log in")

        if login_submitted:
            if not login_username.strip() or not login_password:
                st.warning("Enter your username and password.")
            else:
                try:
                    result = login_user(login_username.strip(), login_password)
                    st.session_state.token = result["access_token"]
                    st.session_state.username = login_username.strip()
                    st.rerun()
                except (requests.RequestException, ValueError) as error:
                    show_error(error)

    with register_tab:
        st.subheader("Create your account")
        with st.form("register_form"):
            new_username = st.text_input("Choose a username")
            new_email = st.text_input("Email address")
            new_password = st.text_input("Choose a password", type="password")
            register_submitted = st.form_submit_button("Create account")

        if register_submitted:
            if not new_username.strip() or not new_email.strip() or not new_password:
                st.warning("Complete all fields.")
            else:
                try:
                    register_user(
                        new_username.strip(),
                        new_email.strip(),
                        new_password,
                    )
                    st.success("Account created! You can now log in.")
                except (requests.RequestException, ValueError) as error:
                    show_error(error)

else:
    token = st.session_state.token
    headers = {"Authorization": f"Bearer {token}"}

    
    with st.sidebar:
        st.subheader("Your account")

        # Show the currently logged-in username
        st.write(f"Logged in as **{st.session_state.username}**")

         # Show profile details from the backend
        try:
            profile = get_profile(token)

            st.write("### My Profile")
            st.write(f"**Username:** {profile.get('username', 'N/A')}")
            st.write(f"**Email:** {profile.get('email', 'N/A')}")

        except (requests.RequestException, ValueError) as error:
            show_error(error)

        if st.button("Log out"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()

    st.header("Create a trip")
    st.write("Enter a trip name, choose your destination, and select your travel dates.")

    if st.session_state.get("trip_created", False):
        st.success("Trip created successfully!")

        if st.button("Create another trip"):
            st.session_state["trip_created"] = False
            st.rerun()


    with st.expander(
        "Create a trip",
        expanded=not st.session_state.get("trip_created", False),
):
        with st.form("create_trip_form"):
            trip_name = st.text_input("Trip name")

            try:
                destinations = get_destinations(token)
            except (requests.RequestException, ValueError) as error:
                show_error(error)
                destinations = []

            if destinations:
                destination_options = {
                    f"{destination['name']} — {destination['city']}, {destination['country']} "
                    f"(ID: {destination['id']})": destination["id"]
                    for destination in destinations
                }
                selected_destination = st.selectbox(
                    "Choose destination",
                    options=list(destination_options.keys()),
                )
                destination_id = destination_options[selected_destination]
            else:
                st.warning("No destinations are available. Please try again.")
                destination_id = None

            start_date = st.date_input("Start date")
            end_date = st.date_input("End date")
            notes = st.text_area("Notes (optional)")
            trip_submitted = st.form_submit_button("Save trip")

        if trip_submitted:
            if not trip_name.strip():
                st.warning("Enter a trip name.")
            elif destination_id is None:
                st.warning("Choose an available destination.")
            elif end_date < start_date:
                st.warning("The end date must be on or after the start date.")
            else:
                trip_data = {
                    "trip_name": trip_name.strip(),
                    "destination_id": int(destination_id),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "notes": notes.strip(),
                }
                try:
                    create_trip(token, trip_data)
                    st.session_state["trip_created"] = True
                    st.success("Trip created successfully!")
                    st.rerun()
                except (requests.RequestException, ValueError) as error:
                    show_error(error)

    st.header("Your trips")
    
    try:
        trips = get_trips(token)

        if isinstance(trips, dict):
            trips = trips.get("trips", trips.get("items", []))

        if trips:
            for trip in trips:
                trip_id = trip.get("id", trip.get("trip_id"))

                with st.container(border=True):
                    st.subheader(trip.get("trip_name", "Untitled trip"))
                    st.write(f"Destination ID: {trip.get('destination_id', 'N/A')}")
                    st.write(f"Start date: {trip.get('start_date', 'N/A')}")
                    st.write(f"End date: {trip.get('end_date', 'N/A')}")
                    st.write(f"Notes: {trip.get('notes') or 'None'}")

                    if trip_id is not None:
                        edit_key = f"edit_trip_{trip_id}"
                        delete_key = f"delete_trip_{trip_id}"

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("Edit trip", key=edit_key):
                                st.session_state[f"editing_trip_{trip_id}"] = True

                        with col2:
                            if st.button("Delete trip", key=delete_key):
                                st.session_state[f"confirm_delete_{trip_id}"] = True

                        if st.session_state.get(f"confirm_delete_{trip_id}", False):
                            st.warning("Are you sure you want to delete this trip?")

                            confirm_col, cancel_col = st.columns(2)

                            with confirm_col:
                                if st.button("Yes, delete", key=f"confirm_{trip_id}"):
                                    try:
                                        delete_trip(token, trip_id)
                                        st.session_state.pop(f"confirm_delete_{trip_id}", None)
                                        st.success("Trip deleted.")
                                        st.rerun()
                                    except (requests.RequestException, ValueError) as error:
                                        show_error(error)

                            with cancel_col:
                                if st.button("Cancel", key=f"cancel_{trip_id}"):
                                    st.session_state.pop(f"confirm_delete_{trip_id}", None)
                                    st.rerun()

                        if st.session_state.get(f"editing_trip_{trip_id}", False):
                            with st.form(f"edit_form_{trip_id}"):
                                edited_name = st.text_input(
                                    "Trip name",
                                    value=trip.get("trip_name", ""),
                                )
                                edited_destination = st.number_input(
                                    "Destination ID",
                                    min_value=1,
                                    value=int(trip.get("destination_id") or 1),
                                )
                                edited_start = st.date_input(
                                    "Start date",
                                    value=__import__("datetime").date.fromisoformat(
                                        str(trip["start_date"])[:10]
                                    ),
                                )
                                edited_end = st.date_input(
                                    "End date",
                                    value=__import__("datetime").date.fromisoformat(
                                        str(trip["end_date"])[:10]
                                    ),
                                )
                                edited_notes = st.text_area(
                                    "Notes",
                                    value=trip.get("notes") or "",
                                )

                                save_edit = st.form_submit_button("Save changes")
                                cancel_edit = st.form_submit_button("Cancel editing")

                            if save_edit:
                                if not edited_name.strip():
                                    st.warning("Enter a trip name.")
                                elif edited_end < edited_start:
                                    st.warning("The end date must be on or after the start date.")
                                else:
                                    updated_data = {
                                        "trip_name": edited_name.strip(),
                                        "destination_id": int(edited_destination),
                                        "start_date": edited_start.isoformat(),
                                        "end_date": edited_end.isoformat(),
                                        "notes": edited_notes.strip(),
                                    }
                                    try:
                                        update_trip(token, trip_id, updated_data)
                                        st.session_state.pop(
                                            f"editing_trip_{trip_id}", None)
                                        
                                        st.success("Trip updated.")
                                        st.rerun()
                                    except (requests.RequestException, ValueError) as error:
                                        show_error(error)

                            if cancel_edit:
                                st.session_state.pop(f"editing_trip_{trip_id}", None)
                                st.rerun()
        else:
            st.info("You haven't created any trips yet.")

    except (requests.RequestException, ValueError) as error:
        show_error(error) 

    
                
    st.divider()
    st.header("Ask TravelWise AI")
    st.write("Ask a question about travel information in the knowledge base.")

    with st.form("travel_question_form"):
        question = st.text_area(
            "Your travel question",
            placeholder="What are some popular attractions in Chicago?",
        )
        question_submitted = st.form_submit_button("Ask AI")

    if question_submitted:
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            with st.spinner("TravelWise AI is preparing an answer..."):
                try:
                    result = ask_travel_question(question.strip(), token)
                    st.markdown("### Answer")
                    st.write(result.get("answer", "No answer was returned."))

                    sources = result.get("sources", [])
                    if sources:
                        st.markdown("### Sources")
                        for source in sources:
                            st.write(f"- {source}")
                except (requests.RequestException, ValueError) as error:
                    show_error(error)