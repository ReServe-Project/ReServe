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
The app covers a wide range of fitness experiences from Pilates and Yoga for mindful movement, to Dance and Muay Thai for high-energy workouts, and even Shooting Range for those who enjoy focus and precision. Whether it’s your first class or part of your weekly routine, ReServe ensures you spend less time worrying about availability and more time improving your well-being.
For members, ReServe offers convenience, flexibility, and control. You can browse nearby studios, explore class types, view live schedules, and book instantly. Say goodbye to waiting lists and confusing sign-ups. With ReServe, you can seamlessly manage all your bookings, track upcoming sessions, and discover new ways to stay active all in one website.
For instructors, ReServe provides a smarter system to manage class reservations. It streamlines the entire process from tracking attendance and updating schedules to optimizing class capacity. This means smoother operations, happier clients, and more time to focus on what matters most: delivering great fitness experiences.
Ultimately, ReServe connects people with the classes they love, making fitness more accessible, organized, and inspiring for everyone.


II. List of Modules
Main (All):
This module provides the configuration settings and data required for the database seeding process, ensuring that initial or sample data is properly inserted into the system for testing, development, or setup purposes.
Registration Page (All):
The registration page lets users create their own account quickly and securely. When all required fields meet the validation rules, users are directed to the Login page to access their account.
Login (All):
The login page is responsible for verifying user information and ensuring secure access. Only authenticated users are allowed to book classes. Unregistered visitors must create an account and log in before making a reservation.
User Profile (Alifa): 
The user profile page displays user information such as profile picture, display name and username handle. It serves as identification for each user in the website. Users can also edit and update their profile details, allowing them to keep their information accurate.
Landing Page/Home (Khayru)
Serves as the entry point for ReServe, introducing the overall app and seamlessly connects with other modules such as login/register, user profile, search, facility details and history to provide a smooth experience for discovering and reserving sports facilities.
Search Page (Shelia)
Users can easily search, discover, and explore available classes with ReServe’s intuitive search feature. Two dedicated search bars make it simple, one to filter by category and another by location. This helps users find the perfect class anytime and anywhere. By default, classes are sorted by the nearest date, but users can also sort results by price or popularity to match their preferences.
Product Details (Juan):
Displays complete information for a selected class (category, class name, instructor, date & time, price, description, and picture), with a single Book action that proceeds to the Checkout page.
History (Evelyn):
The History feature lets users easily view and manage their past, current, and upcoming class reservations. Users can filter by booking type (upcoming, completed, cancelled) and the “Read More” button that is connected to the Product Details of the class the user booked.
Checkout Page (Maharani) : 
The checkout page lets users fill in their booking details, such as participant information and payment method, before confirming their sports session.

III. Main Product Category Dataset Source
1. Yoga (17) Lifa
2. Pilates (17) Rani
3. Boxing (16) Evelyn
4. Muaythai (17) Juan
5. Dance (17) Shelia
6. Shooting Range (16) Khay

The ReServe dataset contains organized information about various fitness classes available within the application. Each record represents a specific class, detailing its category, instructor, schedule, price, description, and associated image. The dataset serves as the foundation for the app’s search, discovery, and booking features, enabling users to easily browse through available sessions and make reservations based on their interests and availability.

The dataset includes several popular class categories offered through ReServe. These categories are Yoga, Pilates, Boxing, Muay Thai, Dance, and Shooting Range. All classes are defined by attributes such as class name, category, instructor, date and time, location, price, and description. A composite primary key made up of instructor, date and time, and location guarantees that each class record is unique and prevents duplication within the database.

Through this structured dataset, ReServe ensures that all class-related data is systematically organized and easily retrievable. It helps maintain smooth functionality across the app, from displaying class listings on the search page to handling bookings, cancellations, and user reviews. This makes the dataset a crucial component in supporting ReServe’s mission to provide a seamless and enjoyable fitness booking experience for users (members) and instructors alike.

Sources:
ClassPass
YogaFit
DanceLifeX
Superprof
Fithub
SigSauerAcademy
StrongBee 

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
        https://pbp.cs.ui.ac.id/web/project/khayru.rafa/reserve
- Design:
        https://www.figma.com/team_invite/redeem/ofrpzmgVMDOn9n8CVpSdHt 
