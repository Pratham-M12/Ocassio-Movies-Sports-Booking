import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/home/')
      .then(res => setEvents(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="App">
      <h1>Event Planner</h1>
      <ul>
        {events.map(event => (
          <li key={event.id}>
            <strong>{event.title}</strong> - {event.location}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
