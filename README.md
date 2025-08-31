## Firebase backend with Unity (iOS client)

This repo scaffolds a Firebase backend (Cloud Functions, Firestore, Storage) and provides Unity iOS client setup notes.

### Prerequisites
- Node.js 20+
- Firebase CLI (`npm i -g firebase-tools`)
- Xcode (for iOS), Unity 2021+ with iOS Build Support

### Configure Firebase project
1. Replace `your-firebase-project-id` in `.firebaserc` with your project id.
2. Login: `firebase login`.
3. Initialize (if needed): `firebase use your-firebase-project-id`.

### Deploy rules and functions
```
cd functions && npm install && npm run build && cd ..
firebase deploy --only firestore:rules,storage:rules,functions
```

### Unity iOS setup
1. Install Firebase Unity SDKs:
   - Download the Firebase Unity SDK and import packages: Auth, Firestore, Functions, Storage.
2. Add your iOS app in Firebase console and download `GoogleService-Info.plist`.
3. In Unity, place `GoogleService-Info.plist` under `Assets/StreamingAssets/`.
4. Build for iOS, then open Xcode project and add `GoogleService-Info.plist` if not auto-copied. Ensure Swift support is added (an empty Swift file may be needed) and enable `Always Embed Swift Standard Libraries` as needed.

### Unity sample code (C#)
Auth sign-in (anonymous):
```csharp
using Firebase;
using Firebase.Auth;
using UnityEngine;

public class AuthSample : MonoBehaviour {
  FirebaseAuth auth;
  async void Start() {
    await FirebaseApp.CheckAndFixDependenciesAsync();
    auth = FirebaseAuth.DefaultInstance;
    await auth.SignInAnonymouslyAsync();
    Debug.Log($"Signed in: {auth.CurrentUser?.UserId}");
  }
}
```

Firestore read/write:
```csharp
using Firebase.Firestore;
using System.Threading.Tasks;

public class FirestoreSample {
  FirebaseFirestore db = FirebaseFirestore.DefaultInstance;
  public async Task WriteUser(string uid) {
    await db.Document($"users/{uid}").SetAsync(new { hello = "world" });
  }
}
```

Call HTTPS function:
```csharp
using Firebase.Functions;
using System.Threading.Tasks;

public class FunctionsSample {
  FirebaseFunctions functions = FirebaseFunctions.DefaultInstance;
  public async Task<string> Hello() {
    var result = await functions.GetHttpsCallable("helloWorld").CallAsync(null);
    return result.Data.ToString();
  }
}
```

Storage upload to user folder:
```csharp
using Firebase.Storage;
using System.Threading.Tasks;

public class StorageSample {
  FirebaseStorage storage = FirebaseStorage.DefaultInstance;
  public async Task Upload(string uid, byte[] bytes) {
    var path = $"userContent/{uid}/image.png";
    var task = storage.GetReference(path).PutBytesAsync(bytes);
    await task;
  }
}
```

### Emulators (local dev)
```
cd functions && npm install && npm run build && cd ..
firebase emulators:start --only functions,firestore,storage
```

In Unity, set emulator hosts as needed (iOS requires localhost via device mapping or using your machine IP).

### Notes
- Update security rules to your data model.
- Consider App Check for Production.
- Use Callable Functions for server logic callable from Unity.
# CortexAI

## Product Description

CortexAI is a modular AI platform designed to streamline the development, deployment, and scaling of intelligent applications. With a focus on flexibility and collaboration, CortexAI supports a variety of AI workflows, including data preprocessing, model training, evaluation, and deployment. By organizing core components into dedicated directories, CortexAI allows teams to work efficiently and securely on different aspects of the platform.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/psychicDree/CortexAI.git
    cd CortexAI
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Setup Environment**
    - Copy `.env.example` to `.env` and fill in the required environment variables.

4. **Run the Application**
    ```bash
    python main.py
    ```
    *(Adjust the entry point as needed for your project structure)*

## Team Access Structure

Different teams have access to different folders within CortexAI to maintain security and workflow clarity:

- **Data Science Team**
  - Access: `/data`, `/notebooks`, `/models`
  - Responsibilities: Data preprocessing, exploratory analysis, model development

- **Backend/DevOps Team**
  - Access: `/api`, `/services`, `/infra`
  - Responsibilities: API development, service orchestration, deployment scripts

- **Frontend Team**
  - Access: `/frontend`, `/ui`
  - Responsibilities: User interface development, user experience enhancements

- **QA/Testing Team**
  - Access: `/tests`, `/mock_data`
  - Responsibilities: Automated testing, quality assurance

> _Note: Folder names above are examples. Please update them to match your actual project structure and access policies._

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
