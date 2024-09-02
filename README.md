## Prerequisites

- Python 3.9 or later
- PostgreSQL database
- Virtual environment (recommended)

## Getting Started

1. **Clone the Repository:**
   
   Clone the project repository to your local machine:
   
   ```shell
   git clone https://github.com/YounoussaBen/farming_livestock_core.git
   ```

2. **Create a Virtual Environment:**
   
   Navigate to the project directory and create a virtual environment:

   ```shell
   cd project
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment:**
   
   On Windows:

   ```shell
   Set-ExecutionPolicy Unrestricted -Scope Process
   ```   
   ```shell
   venv\Scripts\activate
   ```

   On macOS/Linux:

   ```shell
   source venv/bin/activate
   ```

4. **Install Dependencies:**
   
   Install the required dependencies using the provided `requirements.txt` file:

   ```shell
   pip install -r requirements.txt
   ```

5. **Configure the Environment Variables:**
   
   Update the `.env.example` file with your configuration and rename it to `.env`. Fill in the necessary details such as the secret key and database configuration:

6. **Make Migrations:**
   
   Apply the database migrations to set up the database schema:

   ```shell
   python manage.py makemigrations

   python manage.py migrate
   ```

7. **Create a Superuser:**
   
   Create a Django superuser for accessing the admin panel:

   ```shell
   python manage.py createsuperuser
   ```

8. **Run the Development Server:**
   
   Start the Django development server:

   ```shell
   python manage.py runserver
   ```

## Accessing the Application

- Once the server is running, you can access the admin panel at: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Log in using the superuser credentials you created in step 7.

## Swagger UI

To access the Swagger UI:

1. Log in to the admin panel as a superuser.
2. Visit [http://localhost:8000/swagger/](http://localhost:8000/swagger/) to access the Swagger UI for API documentation.

## Contributing

Feel free to contribute to the project! Please follow the coding standards and guidelines as specified in the project.

## License

This project is licensed under the MIT License.
