# GramShiksha: Providing Fast Education To Remotest Places

## Index
| #  | Section Title                                             |
|----|-----------------------------------------------------------|
| 1  | [Theme Chosen](#theme-chosen)                             |
| 2  | [Project Overview](#project-overview)                     |
| 3  | [Considerations](#some-considerations-before-we-begin)     |
| 4  | [Identified Problems](#what-are-the-problems)             |
| 5  | [Focus Areas](#our-focus-considering-these-problems)      |
| 6  | [Unique Selling Propositions](#our-unique-selling-propositions-usps) |
| 7  | [Project Modules](#with-these-things-in-mind-we-have-divided-our-project-into-2-parts) |
| 8  | [Live Streaming Module](#1--low-latency-and-low-data-live-streaming-of-lectures) |
| 9  | [Engagement Enhancer Module](#2--engagement-enhancer-module-low-data-ai-resource-generation) |
| 10 | [Uniqueness of Our Solution](#uniqueness-of-our-solution)  |
| 11 | [User Flow](#user-flow)                                   |
| 12 | [Overall Flow](#overall-flow)                             |
| 13 | [Business Relevance](#business-relevance)                 |
| 14 | [Frontend Implementation - Student Side](#frontend-implementation---student-side) |
| 15 | [Frontend Implementation - Teacher Side](#frontend-implementation---teacher-side) |


---

## Theme Chosen
![Theme Image](https://github.com/user-attachments/assets/5a1e7ff5-9646-4e46-bc9f-04d3b7008969)

---

## Project Overview
**Title: GramShiksha – Providing Fast Education To Remotest Places**

![Project Title Image](https://github.com/user-attachments/assets/d1d56117-f101-48c8-97ee-a4031ed46e8d)

GramShiksha aims to bridge the gap in remote education by offering low-data, high-impact solutions that enable quality teaching and learning even in underserved areas.

---

## Some Considerations Before We Begin
- **Infrastructure Assumptions:**  
  Teachers are assumed to have sufficient resources/internet and the necessary infrastructure to stream lectures.
- **Educational Outreach:**  
  The project supports remote education until governments or organizations can collect enough data on student demographics and attendance to develop comprehensive infrastructure.

---

## What Are the Problems?
![Problems Overview](https://github.com/user-attachments/assets/97ab097f-6fd8-4694-8a00-f04003520954)

---

## Our Focus Considering These Problems
1. **Provide AI-Generated Resources:**  
   A one-stop solution for teachers and students with AI-generated study materials—saving time and reducing costs compared to physical resources.
2. **Implement Low-Internet Services:**  
   Develop solutions that perform well under limited internet connectivity.
3. **Enhance Engagement (Major Problem in Online Education):**  
   Implement modules to encourage active learning and student participation.
4. **Identify At-Risk Students:**  
   Monitor student performance and engagement to identify those who may require additional support or one-on-one counseling.
5. **Analytics for Decision Making:**  
   Deliver detailed analytics on student demographics and resource usage to inform government and organizational decisions.

---

## Our Unique Selling Propositions (USPs)
![USPs Image](https://github.com/user-attachments/assets/17fe14c4-df98-45d6-b24b-4cf8224605ce)

---

## With These Things in Mind We Have Divided Our Project Into 2 Parts
1. **Live (Low Latency) Streaming Module:**  
   - Uses websockets/WebRTC for low data consumption and real-time interaction.  
   - Enables a classroom experience where teachers conduct live sessions with effective human interaction.
2. **Pre-Recorded Lecture & Engagement Enhancer Module:**  
   - Utilizes AWS CDN for efficient video playback with low data usage.  
   - Provides AI-generated resources and engagement tools to boost learning interest.

---

## 1) Low Latency and Low Data Live Streaming of Lectures
![Live Streaming](https://github.com/user-attachments/assets/b5523acc-8b3d-4441-89e0-ac4326f7a093)

---

## 2) Engagement Enhancer Module (Low Data, AI Resource Generation)
![Engagement Enhancer](https://github.com/user-attachments/assets/aafa9723-c2b1-4045-a1a0-e4e9f650b791)

---

## Uniqueness of Our Solution
1. **Lower Internet Consumption for Live Streams:**  
   - Remote online classes consume just **60-100 MB** per hour compared to the typical 600 MB-1 GB.
2. **Efficient AI Resource Generation and Retrieval:**  
   - AI-generated resources are stored on AWS DynamoDB and AWS S3, minimizing data usage on the student side.
3. **Adaptive Learning Quiz Module:**  
   - The quiz system adapts difficulty based on previous answers, ensuring personalized learning.
4. **Individual Attention and Counseling:**  
   - Analytics on engagement and attendance help teachers identify and support weaker students through one-on-one sessions.
5. **Visualization of Key Concepts:**  
   - AI generates images to help students visualize important concepts.
6. **After-Class Comprehensive Notes:**  
   - AI-generated notes, mind maps, and flowcharts provide streamlined post-lecture reviews.
7. **RAG-Based Doubt Assistant:**  
   - A RAG-based chatbot addresses student queries promptly.
8. **Vocational Learning AI Avatar:**  
   - Assists students with career choices, personality development, and vocational learning.

---

## User Flow
![ai_agent (1)](https://github.com/user-attachments/assets/1fbe0be3-3cc6-456b-8a9b-138fb74f4107)

---

## Proposed Solution Flow

Following is the proposed flow of our solution demonstrating the student & teacher side as well as their individual features and use of custom made Aixplain agents in the same.

<p align="center">
  <img src="https://github.com/user-attachments/assets/7d5e6792-aaaf-4b4c-9c49-f2ff0f548639" alt="Proposed Solution Flow 1" width="49%">
  <img src="https://github.com/user-attachments/assets/58c049f9-2665-48db-a937-f89b871b160e" alt="Proposed Solution Flow 2" width="49%">
</p>

---


## AI Agent Creation Methodology

We have developed 5 custom made Aixplain agents and integrated them in various segments of our system. Following is a detailed description of the same.

![image](https://github.com/user-attachments/assets/e732451d-1ab3-4659-b061-0a92c775af21)


---

## Overall Flow
- **Continuous Interaction:**  
  Live classes and stored resources ensure ongoing teacher-student engagement.
- **Data-Driven Teaching:**  
  Teachers adjust strategies based on detailed student interaction data.
- **Efficient Resource Access:**  
  Students enjoy quick, low-data access to AI-generated resources.
- **Government Insight:**  
  Collected data assists in making informed decisions for infrastructural improvements in remote areas.

---

## Business Relevance
![Business Relevance](https://github.com/user-attachments/assets/2e0270c1-6314-4957-b769-20752dc4a751)

---

## Frontend Implementation - Student Side
- **Cover Page:**  
  ![Cover Page](https://github.com/user-attachments/assets/80dc8a13-bcd3-4715-aff8-09ef858448f1)
- **Dashboard:**  
  ![Dashboard](https://github.com/user-attachments/assets/e72bb09a-73e6-4c56-aeab-68edc4e1bace)
- **Live Class Interface:**  
  ![Live Class](https://github.com/user-attachments/assets/1b37ae5a-0b01-47fc-b01b-733edbe7ec8c)
- **Websockets low latency screen sharing alternative:**  
  ![Additional Resource](https://github.com/user-attachments/assets/ffcadd87-292c-48cf-bd76-5f45c7205371)
- **Video/Audio Playback:**  
  ![Video Audio](https://github.com/user-attachments/assets/57926557-860c-4201-b3e2-7efeea31f860)
- **Lecture Selection (e.g., Maths):**  
  ![Lecture Selection](https://github.com/user-attachments/assets/a8dee461-b37c-4b54-801d-f6ab7763b56b)
- **Multilingual Translations:**  
  ![Multilingual](https://github.com/user-attachments/assets/67fff6ab-64c4-4084-8a62-9435fd94997d)
- **Video with Live Quiz:**  
  ![Live Quiz](https://github.com/user-attachments/assets/1f9ea4da-c21b-4aa2-bedc-f8a249320654)
- **Chat with Images and Doubt Resolution:**  
  ![Chat](https://github.com/user-attachments/assets/47b72947-9a34-412d-9a1c-b22ef814d9d7)  
  ![Chat Additional](https://github.com/user-attachments/assets/af45b976-f2a7-4def-a818-83e5b2aa295a)
- **AI-Generated Notes Sample:**  
  [View Sample](https://drive.google.com/file/d/11nxv9hMeBDFH65ZhKDf3PM3FCVirDgnq/view?usp=sharing)  
  ![Notes Sample](https://github.com/user-attachments/assets/b2aaa24c-6034-4799-9c3b-19d3a3f0b4a8)
- **AI-Generated Mindmaps:**  
  ![Mindmaps](https://github.com/user-attachments/assets/36bc9be2-c8b2-4b66-b63d-b68e7f1184ec)


---

## Frontend Implementation - Teacher Side
- **Teacher Dashboard:**  
  ![Teacher Dashboard](https://github.com/user-attachments/assets/0fe08347-d978-45f9-a392-9db637766779)
- **Language Support & Meeting Link:**  
  ![Language & Meeting](https://github.com/user-attachments/assets/905c6aa2-a222-4109-b14a-48dfd85a1647)
- **Lecture Upload and Resource Access:**  
  ![Upload & Resources](https://github.com/user-attachments/assets/21d4c676-cf75-40a3-b9ca-5146f62cbb30)
- **Student Analytics & Engagement Scores:**  
  ![Analytics](https://github.com/user-attachments/assets/8abea242-a0ee-47aa-9abf-4e98ef79f094)
- **View AI-Generated Resources:**  
  ![AI Resources](https://github.com/user-attachments/assets/82d9db89-99e5-4a99-92c9-477467d707cc)
- **Generated Images, Notes, Flowcharts:**  
  ![Visual Aids](https://github.com/user-attachments/assets/d4688dd2-7a2d-49c5-bdda-ad2101ceeee6)


