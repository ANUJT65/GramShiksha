import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar2 from '../components/Navbar2';
import StudentClassChat from '../components/StudentClassChat';
import StudentClassPoll from '../components/StudentClassPoll';
import { IoMdArrowRoundBack } from "react-icons/io";

const RecordedLecturePage = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isChatVisible, setIsChatVisible] = useState(true);
  const [showPopup, setShowPopup] = useState(false);
  const toggleDropdown = () => setIsOpen(!isOpen);
  const navigate = useNavigate();

  const handleButtonClick = (action) => {
    switch (action) {
      case 'View Notes':
        window.open(JSON.parse(videoDetails.notes).pdf_url, '_blank');
        break;
      case 'View Mindmaps':
        setShowPopup(true);
        break;
      case 'Vocational Learning Module':
        navigate(`/student/vocational-learning/${id}`);
        break;
      default:
        alert(`Selected: ${action}`);
    }
    setIsOpen(false);
  };  

  const { id } = useParams();
  const [videoDetails, setVideoDetails] = useState(null);
  const [currentIllustrationIndex, setCurrentIllustrationIndex] = useState(0);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const fetchVideoDetails = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/dy_db/get_video_details/${id}`);
        setVideoDetails(response.data);
      } catch (error) {
        console.error('Error fetching video details:', error);
      }
    };

    const fetchTranscription = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/dy_db/transcript/${id}`);
        const transcriptionText = response.data.transcript;
        await axios.post('http://localhost:5000/chat_bot/set_transcription', {
          transcription_text: transcriptionText,
        });
      } catch (error) {
        console.error('Error fetching or setting transcription:', error);
      }
    };

    fetchVideoDetails();
    fetchTranscription();
  }, [id]);

  useEffect(() => {
    if (videoDetails && videoDetails.image_links) {
      const interval = setInterval(() => {
        setCurrentIllustrationIndex((prevIndex) => {
          const newIndex = (prevIndex + 1) % Object.keys(videoDetails.image_links).length;
          handleSendMessage(`Illustration: ${Object.keys(videoDetails.image_links)[newIndex]}`, Object.values(videoDetails.image_links)[newIndex]);
          return newIndex;
        });
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [videoDetails]);

  const handleSendMessage = (text, imageUrl) => {
    const message = { sender: 'system', text, imageUrl };
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  const closePopup = () => {
    setShowPopup(false);
  };

  if (!videoDetails) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar2 />

      <div className="container mx-auto px-4 py-6">
        {/* Flex container for Back and Options buttons */}
        <div className="flex flex-col md:flex-row justify-between mb-4">
          {/* Back Button */}
          <button
            className="bg-[#2F4550] text-white flex items-center gap-2 px-4 py-2 rounded-md shadow-md hover:bg-[#1E2E38] transition mb-4 md:mb-0"
            onClick={() => navigate(-1)}
          >
            <IoMdArrowRoundBack className="text-lg" />
            Back to Recorded Lectures
          </button>

          {/* Options Dropdown Button */}
          <div className="relative">
            <button
              className="bg-[#CE4760] text-white px-6 py-3 rounded-lg shadow-md hover:bg-[#B03A50] transition"
              onClick={toggleDropdown}
            >
              Options
            </button>

            {isOpen && (
              <div
                className="absolute right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-xl w-56 z-50"
                onClick={(e) => e.stopPropagation()}
              >
                {[
                  'View Notes',
                  'View Mindmaps',
                  'Vocational Learning Module',
                  'Toggle Chat'
                ].map((action) => (
                  <button
                    key={action}
                    className="w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors duration-200 text-gray-700"
                    onClick={() =>
                      action === 'Toggle Chat'
                        ? setIsChatVisible(!isChatVisible)
                        : handleButtonClick(action)
                    }
                  >
                    {action}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-12 gap-4">
          {/* Left side - Video Section */}
          <div className="col-span-12 md:col-span-8">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <video controls className="w-full h-full object-cover">
                <source src={videoDetails.video_url} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>

          {/* Right side - Quiz and Chat */}
          <div className="col-span-12 md:col-span-4">
            <div className="grid grid-cols-1 gap-4">
              {/* Quiz Section - Using StudentClassPoll component directly */}
              <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <StudentClassPoll />
              </div>
              
              {/* Chat Section */}
              {isChatVisible && (
                <div className="bg-white rounded-xl shadow-lg h-[400px]">
                  <div className="flex justify-between items-center px-4 py-2 border-b border-gray-200">
                    <h3 className="font-semibold">Chat</h3>
                  </div>
                  <div className="h-[355px]">
                    <StudentClassChat messages={messages} setMessages={setMessages} />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {showPopup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto relative p-6">
            <button
              className="sticky top-0 right-0 text-red-500 hover:text-red-700 text-4xl font-bold"
              onClick={closePopup}
            >
              &times;
            </button>

            <div className="grid md:grid-cols-1 gap-6">
              {videoDetails.mind_map.urls.map((url, index) => (
                <div
                  key={index}
                  className="bg-gray-100 rounded-lg overflow-hidden shadow-md"
                >
                  <img
                    src={url}
                    alt={`Mind Map ${index + 1}`}
                    className="w-full h-auto object-cover"
                  />
                  <div className="text-center py-3 text-gray-700 font-semibold">
                    Mind Map {index + 1}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecordedLecturePage;