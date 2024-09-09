Here's the translated document in English:

# Face++ Face Detection Configuration Document

[Face++ Official Documentation](https://console.faceplusplus.com.cn/documents/4888373)

## 1. Register a Face++ Account
To use the Face++ Face Detection API, you first need to register an account on the Face++ official website. After registration, you will be able to access the API console and related services.

### Steps:
1. Visit the [Face++ Official Website](https://www.faceplusplus.com.cn/).
2. Click the "Register" button and fill in the relevant information to create your account.

## 2. Obtain API KEY and API SECRET
After registering and logging in, you need to obtain the API Key and API Secret for authentication. This information is necessary for calling the API.

### Steps:
1. Log in to your Face++ account.
2. Go to Console -> Application Management -> API Key.
3. In the console, you will see your API Key and API Secret.

## 3. Set Environment Variables
To securely use the API Key and API Secret in your code, it is recommended to set them as environment variables. This avoids hardcoding sensitive information in your code.

### Steps to Set Environment Variables on Different Operating Systems:
- **Windows**:
    1. Open the Command Prompt.
    2. Enter the following commands and press Enter:
       ```cmd
       set FACE_PLUS_API_KEY="Your_API_KEY"
       set FACE_PLUS_API_SECRET="Your_API_SECRET"
       ```

- **Linux / macOS**:
    1. Open the terminal.
    2. Enter the following commands and press Enter:
       ```bash
       export FACE_PLUS_API_KEY="Your_API_KEY"
       export FACE_PLUS_API_SECRET="Your_API_SECRET"
       ```

> **Note**: You may need to run the above commands before starting your application, or add these commands to your shell configuration file (e.g., `.bashrc` or `.bash_profile`) so that they are automatically loaded each time you start the terminal.

## 4. Start Gradio Service
Run the Gradio service, and select "face++" in the "Face Detection Model".

```bash
python app.py
```

![alt text](../assets/face++.png)

## Explanation of error codes

https://console.faceplusplus.com.cn/documents/4888373