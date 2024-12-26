# Library Management System

This project is a Library Management System built with Django. It allows users to manage and search for academic papers. The system includes features such as uploading papers, generating AI summaries, and searching through the papers using a custom search implementation.

## Features

- Upload and manage academic papers
- Generate AI summaries for papers
- Search for papers using custom search implementation
- View detailed information about each paper
- Download paper files

## Technologies Used

- Django
- Haystack
- Bootstrap 5

## Installation

1. Clone the repository:

```sh
git clone https://github.com/fe-bit/library.git
cd library
```

2. Create and activate a virtual environment:

```ssh
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

3. Install the required packages:

````ssh
pip install -r requirements.txt
```

4. Set up the database:

````ssh
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:

````ssh
python manage.py createsuperuser
```

6. Run the development server:

````ssh
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/.

# Usage
## Uploading Papers
1. Log in to the admin panel at http://127.0.0.1:8000/admin/.
2. Add a new paper by filling in the required fields and uploading a PDF file.
3. Save the paper to generate the AI summary and index it for search.
## Searching for Papers
1. Use the search bar on the home page to search for papers by title, authors, year, or further information.
2. View the search results and click on a paper title to see detailed information.
## Viewing Paper Details
1. Click on a paper title in the search results or paper list to view detailed information about the paper.
2. The details page includes the title, authors, year, URL, further information, AI summary, and a download link for the file.
# Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

# License
This project is licensed under the MIT License. See the LICENSE file for details.