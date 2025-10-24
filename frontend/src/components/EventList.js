// EventList.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function EventList() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    axios.get('/api/events/')
      .then(res => setEvents(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="container mt-4">
      <h2>Upcoming Events</h2>
      <div className="row">
        {events.map(event => (
          <div className="col-md-4" key={event.id}>
            <div className="card mb-3">
              <div className="card-body">
                <h5 className="card-title">{event.title}</h5>
                <p>{event.date} | {event.location}</p>
                <a href={`/events/${event.id}`} className="btn btn-primary">Details</a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default EventList;