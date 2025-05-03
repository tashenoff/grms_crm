'use client';
import React from 'react';
import LeadCard from './LeadCard';

export default function LeadList({ leads, onSelect }) {
  if (!leads || !Array.isArray(leads)) {
    // Handle cases where leads is not an array (e.g., loading, error)
    return <div className="text-center py-4 text-gray-500">Загрузка лидов...</div>; 
  }

  if (leads.length === 0) {
    return <div className="text-center py-4 text-gray-500">Нет заявок</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {leads.map(lead => (
        <LeadCard key={lead.id} lead={lead} onSelect={onSelect} />
      ))}
    </div>
  );
}
