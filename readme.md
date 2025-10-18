Group member names
1. Alifa Izzatunnisa Elqudsi Prabowo 2406365212
2. Evelyne Octaviana Benedicta Aritonang 2406365282
3. Juansao Fortunio Tandi 2406365345
4. Khayru Rafa Kartajaya 2406365263
5. Maharani Anindya Budiarti 2406365300
6. Shelia Vellicita 2406453606

I. Application Description

Tired of the same workout routine? Meet ReServe, the app that helps you move, sweat, and explore fitness your way!

ReServe is a smart class booking app designed to make joining fitness sessions simple, fast, and stress-free. With fitness classes like Pilates, Yoga, and Boxing becoming increasingly popular, spots can fill up within minutes. ReServe solves this problem by giving users real-time access to available classes and studios, allowing them to easily find and reserve sessions anytime, anywhere.

The app covers a wide range of fitness experiences from Pilates and Yoga for mindful movement, to Dance and Muay Thai for high-energy workouts, and even Ice Skating for balance, grace, and full-body coordination. Whether it’s your first class or part of your weekly routine, ReServe ensures you spend less time worrying about availability and more time improving your well-being.

For members, ReServe offers convenience, flexibility, and control. You can browse nearby studios, explore class types, view live schedules, and book instantly. Say goodbye to waiting lists and confusing sign-ups. With ReServe, you can seamlessly manage all your bookings, track upcoming sessions, and discover new ways to stay active all in one website.

For instructors, ReServe provides a smarter system to manage class reservations. It streamlines the entire process from tracking attendance and updating schedules to optimizing class capacity. This means smoother operations, happier clients, and more time to focus on what matters most: delivering great fitness experiences.

Ultimately, ReServe connects people with the classes they love, making fitness more accessible, organized, and inspiring for everyone.


II. List of Modules

1. Main (All):

This module provides the configuration settings and data required for the database seeding process, ensuring that initial or sample data is properly inserted into the system for testing, development, or setup purposes.


2. Registration Page (All):

The registration page lets users create their own account quickly and securely. When all required fields meet the validation rules, users are directed to the Login page to access their account.


3. Login (All):

The login page is responsible for verifying user information and ensuring secure access. Only authenticated users are allowed to book classes. Unregistered visitors must create an account and log in before making a reservation.


4. User Profile (Juan): 

The user profile page displays user information such as profile picture, display name and username handle. It serves as identification for each user in the website. Users can also edit and update their profile details, allowing them to keep their information accurate.


5. Landing Page/Home & Search (Maharani)

Serves as the central entry point for ReServe, introducing the app and immediately empowering users to discover and reserve sports facilities through its intuitive search feature. Users can easily explore available classes using two dedicated search bars to filter by category (like yoga, pilates, or boxing). By default, results are sorted by the nearest date, but users can also sort by price or popularity to find the perfect class anytime, anywhere. This homepage seamlessly connects with all other modules, such as user profiles, facility details, and history, to provide a smooth and integrated experience from discovery to reservation.


6. Blog (Shelia)

The Blog module serves as ReServe's fitness and wellness hub, where users can read and discover valuable content. It features articles, tutorials for classes like yoga and boxing, healthy living tips, and community stories. This space supports users beyond bookings, providing knowledge to help them learn, stay motivated, and get the most out of their wellness journey.


7. Product Details (Alifa):

Displays complete information for a selected class (category, class name, instructor, date & time, price, description, and picture), with a single Book action that proceeds to the Checkout page.


8. Personal Goals (Khayru):

The Personal Goals module is a personal tracker where users can set and manage their fitness objectives. Users can create a new goal by clicking a date on the calendar, read all their previously made goals, and update a goal's status by clicking a checkbox to visually cross it out as complete.


9. Checkout Page & History (Evelyn) : 

The checkout page lets users fill in their booking details, such as participant information and payment method, before confirming their sports session. Once a booking is complete, the History feature allows users to easily view and manage all their past, current, and upcoming class reservations. Within the History module, users can filter by booking type (upcoming, completed, cancelled) and use the “Read More” button to revisit the Product Details of any class they booked.


III. Main Product Category Dataset Source
1. Yoga (17) Alifa
2. Pilates (17) Maharani
3. Boxing (16) Evelyn
4. Muaythai (17) Juan
5. Dance (17) Shelia
6. Ice Skating (16) Khayru

The ReServe dataset contains organized information about various fitness classes available within the application. Each record represents a specific class, detailing its category, instructor, schedule, price, description, and associated image. The dataset serves as the foundation for the app’s search, discovery, and booking features, enabling users to easily browse through available sessions and make reservations based on their interests and availability.

The dataset includes several popular class categories offered through ReServe. These categories are Yoga, Pilates, Boxing, Muay Thai, Dance, and Ice Skating. All classes are defined by attributes such as class name, category, instructor, date and time, location, price, and description. A composite primary key made up of instructor, date and time, and location guarantees that each class record is unique and prevents duplication within the database.

Through this structured dataset, ReServe ensures that all class-related data is systematically organized and easily retrievable. It helps maintain smooth functionality across the app, from displaying class listings on the search page to handling bookings, cancellations, and user reviews. This makes the dataset a crucial component in supporting ReServe’s mission to provide a seamless and enjoyable fitness booking experience for users (members) and instructors alike.

ReServe Dataset Link:
https://docs.google.com/spreadsheets/d/1-QbXl7YVeG_cRdmo75v3SZpMip6Rkg6Ryo4JfBy-b_I/edit?usp=drivesdk

- Sources:
    - ClassPass - https://classpass.com/
    - YogaFit - https://www.yogafitid.com/class
    - DanceLifeX - https://www.dancelifex.id/class
    - Superprof - https://www.superprof.co.id/kursus/muay-thai/indonesia/
    - Fithub - https://fithub.id/class
    - SigSauerAcademy - https://sigsaueracademy.com/beginner-courses
    - StrongBee - https://strongbee.co.id/home/classes?search=&location=


IV. User Roles
1. Member
    - Description: 
        Users who want to book fitness classes such as Pilates, Yoga, Dance, Boxing, Muay Thai, or Shooting Range for themselves or their group.
    - Permissions:
        - Create, login, and manage their account.
        - Search for classes by category and location
        - View the number of users who have already booked the class
        - Check the total payment before confirming a booking
        - View booking history
        - Cancel reservation

2. Instructor
    - Description: 
        Users with this role can list and manage their fitness classes or studios on ReServe, making them available for Members to discover and book.
    - Permissions:
        - Create and manage a professional instructor or studio profile
        - Add, edit, and remove classes, including details such as schedule, capacity, price, and location.
        - View real-time insights showing the number of users viewing the class and those who have already booked it.

V. Links
- PWS Deployment:
        https://khayru-rafa-reserve.pbp.cs.ui.ac.id
- Design:
        https://www.figma.com/team_invite/redeem/ofrpzmgVMDOn9n8CVpSdHt 
