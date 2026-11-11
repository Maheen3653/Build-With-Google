
import streamlit as st


def _show_error(error):
    """Display a readable authentication error."""
    message = str(error)

    if "Invalid login credentials" in message:
        st.error("Incorrect email or password.")
    elif "Email not confirmed" in message:
        st.warning(
            "Please verify your email address before logging in."
        )
    elif "Password should be" in message:
        st.error(message)
    else:
        st.error(f"Authentication error: {message}")


def render_auth_page(supabase):
    """Render DataSphere registration and login."""

    st.title("Welcome to DataSphere")
    st.write(
        "Sign in or create an account to save your learning journey."
    )

    login_tab, signup_tab = st.tabs(["Log in", "Create account"])

    # ----------------------------------------------
    # LOGIN
    # ----------------------------------------------

    with login_tab:

        st.subheader("Welcome back")

        with st.form("datasphere_login_form"):

            email = st.text_input(
                "Email address",
                placeholder="you@example.com"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Log in",
                type="primary",
                use_container_width=True
            )

            if submitted:

                if not email.strip() or not password:
                    st.error("Please enter your email and password.")

                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })

                        user = response.user
                        session = response.session

                        if user and session:
                            st.session_state["auth_user"] = {
                                "id": user.id,
                                "email": user.email
                            }

                            st.session_state.pop("profile", None)
                            st.session_state.pop("tracker", None)

                            st.success("Login successful!")
                            st.rerun()

                        else:
                            st.error(
                                "Login could not be completed. "
                                "Please verify your email first."
                            )

                    except Exception as error:
                        _show_error(error)

    # ----------------------------------------------
    # SIGN UP
    # ----------------------------------------------

    with signup_tab:

        st.subheader("Create your account")

        with st.form("datasphere_signup_form"):

            name = st.text_input(
                "Your name",
                placeholder="Enter your name"
            )

            email = st.text_input(
                "Email address",
                placeholder="you@example.com",
                key="signup_email"
            )

            password = st.text_input(
                "Create password",
                type="password",
                key="signup_password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Create account",
                type="primary",
                use_container_width=True
            )

            if submitted:

                if not name.strip() or not email.strip():
                    st.error("Please complete all required fields.")

                elif len(password) < 8:
                    st.error(
                        "Your password must contain at least 8 characters."
                    )

                elif password != confirm_password:
                    st.error("Your passwords do not match.")

                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": email.strip(),
                            "password": password,
                            "options": {
                                "data": {
                                    "full_name": name.strip()
                                }
                            }
                        })

                        if response.user:
                            st.success(
                                "Your account has been created!"
                            )

                            st.info(
                                "We've sent a verification email to "
                                f"{email.strip()}. Please verify your "
                                "email, then return to the Log in tab."
                            )

                        else:
                            st.error(
                                "Account creation could not be completed."
                            )

                    except Exception as error:
                        _show_error(error)


def logout_user(supabase):
    """Sign out and clear user-specific session data."""

    try:
        supabase.auth.sign_out()

    finally:
        keys_to_clear = [
            "auth_user",
            "profile",
            "tracker",
            "generated_projects",
            "ai_cache",
            "_supabase_client",
        ]

        for key in keys_to_clear:
            st.session_state.pop(key, None)

        st.session_state["navigation_choice"] = "Home"
        st.rerun()
