# PolicyCheck

PolicyCheck is an application aimed at making terms of service more understandable and facilitating the tracking and visualization of changes over time.

## Features

- Simplify complex terms of service documents to improve user comprehension.
- Track and compare changes in terms of service over multiple versions.
- Generate visualizations to highlight modifications and make them more accessible.

## Installation

Follow these steps to install and set up PolicyCheck:

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/PolicyCheck.git

Navigate to the project directory:
    
    cd PolicyCheck

Install the dependencies:

    pip install -r requirements.txt

# Usage

## Preparing a policy

```bash
python clean_up.py <input_file.html> <type [reddit | google]> <output_file.html>
```

## Diffing policies

```bash
python mark_diffs.py <old_file.html> <new_file.html> <output_file.html>
```

Old and new file must have been prepared with `clean_up.py`.

Place the result into the same folder as `diff.css` to mark insert, deleted and changed parts.

## Website

To use PolicyCheck, follow these steps:

Launch the application:

    python main.py

Navigate to the web interface by opening your browser and accessing the following URL: http://localhost:8000.

No features are added to the website yet.

# License

This project is licensed under the [MIT License](License).

# Contact

For any questions or inquiries, please contact us.

# Status

PolicyCheck is currently under active development.

## Completed Features

    TBD

## Planned Features

### Summary and Simplification:

* Automatic summarization and categorization of sections in terms of service documents.
* Translation of complex texts into simplified language to improve understandability.
* Highlighting important keywords and phrases.

### Visual Representation:

* Creation of visual diagrams to depict complex relationships and dependencies.
* Graphical visualization of changes over time to make changes more apparent to users.
* Interactive user interface for intuitive navigation and exploration of visualized terms of service.

### Aspect Evaluation:

* Identification and evaluation of important aspects in terms of service, such as privacy, liability limitations, intellectual property, etc.
* Automatic generation of an overview of these aspects with corresponding ratings and explanations.
* Customization of weighting and relevance of aspects based on individual user preferences.

### Global Aspects:

* Examination of common aspects across multiple terms of service to identify patterns and differences.
* Comparison and evaluation of terms of service from different services or platforms to enable informed decisions for users.

### Change Detection:

* Tracking and presentation of changes in terms of service over time.

## Known Issues

    TBD

Please note that the above information is subject to change as the project progresses.