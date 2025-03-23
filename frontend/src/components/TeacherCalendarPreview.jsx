import React, { useState } from 'react';
import axios from 'axios';
import CalendarDate from './CalendarDate';

const TeacherCalendarPreview = () => {
  const [message, setMessage] = useState('');

  const handleSendReminder = async () => {
    try {
      const response = await axios.get('http://localhost:5000/email/send');
      setMessage('Reminder sent successfully!');
    } catch (error) {
      setMessage('Error sending reminder.');
      console.error('Error sending reminder:', error);
    }
  };

  return (
    <div className="col-span-2 py-2 rounded-md px-5 flex flex-col border shadow-md min-h-0">
      <div className="text-xl font-bold">September 2024</div>
      
      {/* calendar */}
      <div className="flex justify-around mt-2 font-semibold">
        <CalendarDate day="Mon" date="23" today={true} />
        <CalendarDate day="Tue" date="24" />
        <CalendarDate day="Wed" date="25" />
        <CalendarDate day="Thur" date="26" />
        <CalendarDate day="Fri" date="27" />
        <CalendarDate day="Sat" date="28" />
      </div>
      
      {/* events */}
      <div className="text-md font-bold mt-4">Upcoming/Ongoing</div>

      <div className="flex justify-between">
        <div>
          <div className="font-bold mt-3">Science Lecture</div>
          <div className="text-[#878787] mt-1">4:00 pm - 5:00 pm</div>
        </div>

        <div className='flex flex-col'>
          <a
            className="mt-4 py-2 px-3 font-bold bg-red-500 text-white mr-2 rounded-md"
            href='https://sync-space-nine.vercel.app'
          >
            Join Live
          </a>
          <button 
            className='bg-black text-white font-bold py-2 px-3 rounded-md mt-2'
            onClick={handleSendReminder}
          >
            Send Reminder
          </button>
        </div>
      </div>

      {message && <div className="mt-2 text-green-500">{message}</div>}

      <hr className="mt-2" />

      {/* Additional Events */}
      <div className="font-bold mt-3">Vocational Exam</div>
      <div className="text-[#878787] mt-1">8:00 pm - 10:00 pm</div>
      <div className="font-bold mt-3">Doubt Session</div>
      <div className="text-[#878787] mt-1">10:00 pm - 11:30 pm</div>
    </div>
  );
};

export default TeacherCalendarPreview;