## CortexAI™ Unity Client

Project scaffold for the CortexAI™ Unity application.

Structure:
- Assets/
  - Scripts/
    - Managers/
    - UI/
    - Voice/
    - Network/
    - Data/
  - Scenes/
  - Prefabs/
  - Resources/

Getting started:
- Open this folder as a Unity project.
- Add scene files under `Assets/Scenes` and set the startup scene in Build Settings.
- Attach `GameManager` to an empty GameObject in your first scene.

Onboarding setup:
- Add empty GameObjects and attach these components in your startup scene:
  - `GameManager`
  - `SessionManager`
  - `UIManager` with references to your `homePanel` and `sessionPanel`
  - `AuthManager`
  - `OnboardingManager` with references to:
    - `AuthManager`
    - `UIManager`
    - `OnboardingUI` (a Canvas panel with Inputs/Buttons)
    - `SignInUI` (a Canvas panel with Buttons)
- Create two Canvas panels:
  - Onboarding panel with:
    - `InputField` for Name -> link to `OnboardingUI.nameInput`
    - `InputField` for Age -> link to `OnboardingUI.ageInput`
    - `Button` Create -> link to `OnboardingUI.createButton`
    - `Button` I am existing user -> link to `OnboardingUI.existingUserButton`
    - `Text` Error -> link to `OnboardingUI.errorText`
  - Sign-in panel with:
    - `Button` Sign In -> link to `SignInUI.signInButton`
    - `Button` Back -> link to `SignInUI.backButton`
    - `Text` Error -> link to `SignInUI.errorText`
- Ensure `OnboardingUI` and `SignInUI` panels are disabled by default in the Hierarchy.
- At runtime, `GameManager` calls `OnboardingManager.StartOnboardingFlow()`:
  - If a user profile exists (stored in PlayerPrefs), user is sent to Home.
  - Otherwise the onboarding panel is shown with name and age fields and a button to redirect to existing user sign-in.

Brand guidelines:
- Visual: calming blues/purples with aqua/neon green highlights.
- Voice: empathetic, supportive, professional. Empower, not diagnose.

