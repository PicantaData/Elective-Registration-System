# Elective-Registration-System


## Overview

The Elective Registration System is designed to facilitate the selection and allotment of elective courses for students at an academic institute. The system aims to streamline the process by allowing students to submit their course preferences and ensuring fair and efficient allotment based on predefined criteria.

## Key Features

#### Student Interface:

*Login and Authentication:* Secure login for students using their institute credentials.  
*Elective Catalog:* Display a comprehensive list of available elective courses with descriptions, prerequisites, and credits.  
*Preference Submission:* Allow students to select and rank their preferred elective courses.  
*Confirmation and Modification:* Enable students to review and modify their preferences before the submission deadline.  

#### Admin Interface:

*Course Management:* Admins can add, update, or remove elective courses and manage course details.  
*Student Management:* Admins can manage student records, including their registration status and course history.  
*Preference Collection:* Collect and view the preferences submitted by students.  
*Allotment Algorithm:* Run the allotment process based on predefined rules and criteria.  
*Reports and Notifications:* Generate reports on allotments and send notifications to students regarding their allocated electives.  

#### Allotment Algorithm:

*Priority-Based Allotment:* Allocate courses based on student preferences and availability, giving priority to higher-ranked choices.  
*Seat Availability:* Ensure that the number of students allotted to a course does not exceed its capacity.  
*Conflict Resolution:* Implement rules to handle conflicts, such as multiple students vying for limited seats in a popular course.  
*Fair Distribution:* Ensure a fair distribution of courses among students, possibly incorporating a random element or lottery system for tie-breaking.  
_A deeper description of the algorithm to be provided later._

*Allotment Results:* Notify students of their allotted courses via email and the student portal.

### Technical Specifications

#### Backend:

*Server-Side Language:* Python  
*Database:* SQLite3 for storing student records, course details, and preferences.  
*Framework:* Django  

#### Frontend:

*Language(s) and Framework:* HTML, CSS, Bootstrap for creating a dynamic and responsive user interface.  
*Design:* User-friendly design with easy navigation and clear instructions.  

*Authentication:* OAuth2 - Google Authentication.

#### Deployment: TBD


The Elective Registration System provides a robust solution to manage elective course selection and allotment efficiently. By leveraging technology to automate and streamline the process, the system enhances the student experience, reduces administrative burden, and ensures a fair and transparent allocation of courses.
