'use client';
import React from 'react';

export default function LeadCard({ lead, onSelect }) {
  // Функция для определения класса статуса
  const getStatusClass = (status) => {
    switch (status) {
      case 'new': 
      case 'processing':
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
      case 'accepted':
        return 'bg-green-100 text-green-800';
      case 'delivery': 
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
      case 'declined':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800'; 
    }
  };

  // Функция для получения текста статуса
  const getStatusText = (status) => {
    switch (status) {
      case 'new':
        return 'Новый';
      case 'processing':
      case 'in_progress':
        return 'В работе';
      case 'completed':
      case 'accepted':
        return 'Выполнен';
      case 'delivery': 
        return 'Доставка';
      case 'cancelled':
      case 'declined':
        return 'Отменен';
      default:
        return status ? status.charAt(0).toUpperCase() + status.slice(1) : 'Неизвестен'; 
    }
  };

  return (
    <div
      onClick={() => onSelect(lead)}
      className="cursor-pointer bg-white rounded-lg p-4 shadow-sm border-l-4 border-blue-500"
    >
      <div className="flex justify-between items-center mb-3">
        <div className="font-semibold text-blue-600">{lead.client_name || 'Клиент'}</div>
        <div className="text-xs text-gray-500">
          {lead.created_at}
          {lead.related_count > 1 ? 
            <span className="ml-2 bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded-full">
              Заказов: {lead.related_count}
            </span> : ''}
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-2 mb-3">
        {lead.phone && <div className="text-sm text-gray-800"><span className="font-medium">📞</span> {lead.phone}</div>}
        {lead.city && <div className="text-sm text-gray-800"><span className="font-medium">🏙️</span> {lead.city}</div>}
        {lead.address && <div className="text-sm text-gray-800"><span className="font-medium">📍</span> {lead.address}</div>}
        {lead.total_amount && <div className="text-sm text-gray-800"><span className="font-medium">💰</span> {lead.total_amount}</div>}
        <div className="text-sm text-gray-800"><span className="font-medium">Источник:</span> {lead.source || '—'}</div>
        <div className="text-sm text-gray-800"><span className="font-medium">Исполнитель:</span> {lead.executor_username || 'Не назначен'}</div>
      </div>
      
      {lead.order_details && (
        <div className="text-sm mb-3">
          <div className="order-details bg-gray-50 p-2 rounded text-xs text-gray-800">
            {lead.order_details.length > 100 ? lead.order_details.substring(0, 100) + '...' : lead.order_details}
          </div>
        </div>
      )}
      
      <div className="flex justify-between items-center mt-2">
        <div>
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusClass(lead.status)}`}>
            {getStatusText(lead.status)}
          </span>
        </div>
      </div>
    </div>
  );
}