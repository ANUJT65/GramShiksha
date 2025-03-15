| #  | Index                                                                                                              |
|----|--------------------------------------------------------------------------------------------------------------------|                                        
| 2  | [Some Considerations](#some-considerations-before-we-begin)                                                        |
| 3  | [Problems](#what-are-the-problems)                                                                                 |
| 4  | [Our Focus Considering These Problems](#our-focus-considering-these-problems)                                       |
| 5  | [Project Division](#with-these-things-in-mind-we-have-divided-our-project-into-2-parts)                             |
| 6  | [Unique Selling Propositions (USPs)](#our-unique-selling-propositions-usps)                                         |
| 7  | [Uniqueness of Our Solution](#uniqueness-of-our-solution)                                                          |
| 8  | [Architecture and Use Cases](#architecture-and-use-cases)                                                          |
| 9  | [Methodology & Technology Stack](#methodology-tech-stack)                                                          |
| 10 | [Research on Low Latency Video Streaming](#our-research-on-low-latency-video-streaming)                             |
| 11 | [Plan Part 1: Smartboard + Pre-Downloaded PPT + Audio](#plan-part-1--smartboard--pre-downloaded-ppt--audio-100mb)   |
| 12 | [Plan Part 2: Engagement Enhancer Module](#plan-part-2--engagement-enhancer-module-major-data-consumption-will-only-be-in-retrieval-of-resources) |
| 13 | [Advantages of Azure CDN for Remote Education](#advantages-of-azure-cdn-for-remote-education)                       |
|14  | [AI-Resource Generation: HOW WE ENSURE EFFICIENT AND LOW DATA CONSUMPTION](#ai-resource-generation-how-we-ensure-efficient-and-low-data-consumption)  |
| 15 | [Low Latency Platform](#low-latency-platform)                                                                      |
| 16 | [Present Implementation](#present-implementation)                                                                  |
| 17 | [Next Implementation](#next-implementation)                                                                  |
| 18 | [BUSINESS RELEVANCE](#BUSINESS-RELEVANCE)                                                                          |
| 19 | [Impact And Benefits](#Impact-And-Benefits)                                                                        |
| 20 | [DEMO VIDEO](#DEMO-VIDEO)                                                                                          |
| 21 | [FeedbackForm](#feedbackform)                                                                                     |




# aixplain

## Theme chosen
![image](https://github.com/user-attachments/assets/5a1e7ff5-9646-4e46-bc9f-04d3b7008969)



# Title: **GramShiksha: Providing Fast Education To Remotest Places**  

![image](https://github.com/user-attachments/assets/d1d56117-f101-48c8-97ee-a4031ed46e8d)



## **Some Considerations before we begin**
- We are assuming that teachers are given sufficient resources/internet and also infra facilities to stream lectures
- Our Understanding is that we are providing remote education to students until government/organizations have enough data on student demographics/attendance etc to provide proper infrastructure to the students.

## **WHAT ARE THE PROBLEMS??**
![image](https://github.com/user-attachments/assets/97ab097f-6fd8-4694-8a00-f04003520954)


## **OUR FOCUS CONSIDERING THESE PROBLEMS**

1. **Provide AI-Generated Resources:** Provide a one-stop solution for teachers and students with AI-generated resources, saving time and cost compared to physical resources.
2. **Implement Low-Internet Services:** Develop solutions that function well with limited internet connectivity.
3. **Enhance Engagement(MAJOR PROBLEM IN ONLINE EDUCATION):** Even if we provide all resources , many students dont really utilize these things, so we have various modules to encourage students to learn.
4. **Identify At-Risk Students:** Help identify students who are weaker, have lower attendance, or are at risk of dropping out and improve engagement by 1 on 1 counselling by teachers.
5. **Analytics for Decision Making:** Provide detailed analytics on student demographics to aid in decision-making and resource allocation by government

## **With these things in mind We have divided our project into 2 parts**
- **1)Live ( low latency ) streaming of video lectures Module with use of websockets/webrtc.**
- Here students will just join classroom and teacher would teach like in a regular meet but through low data consumption and better human interaction.
- **2)PreRecorded Lecture VideoPlayback/Engagement Enhancer Module using Azure CDN( low data consumption)**
- Here there is loads of ai generated resources, engagement enhancing resources which generate interests in learning and all given through lowest data consumption on a prerecorded lecture.



## **Our Unique Selling Propositions (USPs)**
## 1)) LOW LATENCY AND LOW DATA LIVE STREAMING OF LECTURES

![lowlatency](https://github.com/user-attachments/assets/b5523acc-8b3d-4441-89e0-ac4326f7a093)
## 2)) ENGAGEMENT ENHANCER MODULE LOW DATA AI RESOURCE GENERATION
![USP](https://github.com/user-attachments/assets/aafa9723-c2b1-4045-a1a0-e4e9f650b791)



## **UNIQUENESS OF OUR SOLUTION**
![image](https://github.com/user-attachments/assets/17fe14c4-df98-45d6-b24b-4cf8224605ce)





1. **Lower Internet Consumption for Live Steams:(research is given below)**
   - Provides remote online classes using just **60-100 MB** of data per hour, compared to typical 600 MB-1 GB.
1. **AI Resource generation at lowest data and retrieval at lowest latency:(research is given below)**
   - With the use of **Azure CDN** and prestorage of the  ai generated resources in **Azure Blob and MongoDB Atlas** while uploading the video , consumption on student side is reduced, only consumption is for 
     retrieval of databases.
2. **Adaptive Learning Quiz Module:**
   - Developed an adaptive learning quiz system where the difficulty of the next question is determined by previously answered questions.
3. **Individual Attention and Counseling:**
   - Focus on weaker students through engagement, score, and attendance analytics. Offers 1-to-1 counseling and doubt sessions.
4. **Visualization of Key Concepts:**
   - Generation of images related to key concepts, helping students visualize key points.
5. **After-Class Comprehensive Notes:**
   - Streamlined post-lecture review with AI-generated class notes, mind maps, and flowcharts.
6. **RAG-Based Doubt Assistant:**
   - Introduce a RAG-based chatbot trained on platform content to swiftly address student queries.
7. **Vocational Learning AI Avatar:**
   - Helps students choose careers, assists in personality development, and vocational learning.
  
## **USER FLOW**
![SIH2024smalldiagram drawio (4)](https://github.com/user-attachments/assets/d7059509-b558-494e-a98f-6e495eae58ae)

### Teacher Side
- **Online Lecture and Recorded Lecture:**
  - Conduct live classes using smart boards and streaming technologies (e.g., WebRTC).
  - Record lectures for later access; lectures are stored in cloud services (e.g., Azure CDN).

- **Teacher Dashboard:**
  - **Time Table Generation:** Create and manage class schedules.
  - **Student Management:**
    - Generate personal reports for students.
    - Track attendance and monitor student engagement.
    - Send SMS for lectures to parents application.
    - Student Demographics, location and resource management
  - **Feedback Mechanism:** Receive insights on student performance, including dropout risk scores.

- **AI-Generated Resources Storage(RAG BASED ):**
  - AI-generated resources (e.g., images, quizzes) are created once and stored in:
    - **MongoDB:** For structured data storage.
    - **Microsoft Azure Blob Storage:** For storing large files and assets.

### Student Side
- **Engagement Enhancer Module: (ALL RAGS BASED)**
  - **Adaptive Quiz with timely engaement monitoring:** Generate quizzes that adapt in difficulty based on student performance at interval at 2-5 minutes.
  - **Image Generation:** Create visual aids passing relevant keywords and key sentences from viddeo to  Stable Diffusion image generation model.
  - **Mind Map Generation:** Generate mind maps to visualize concepts for better understanding.
  - **AI Avatar:** Provide interactive support for vocational learning and personality development.
  - **Illustrated Notes:** Deliver structured notes including titles, subheadings, summaries, and flowcharts.

### Overall Flow
- Continuous interaction between teachers and students through live classes and stored resources.
- Teachers receive data on student interactions to adjust teaching strategies.
- Students have efficient access to AI-generated resources, enhancing the overall learning experience.
- Government gets data of the students and the resources needed for their better learning experience,
- so that they could enhance the infrastructure in these remote areas.

## **BUSINESS RELEVANCE**
![image](https://github.com/user-attachments/assets/576e8e3e-2945-4e26-91ad-fe35204a5056)

