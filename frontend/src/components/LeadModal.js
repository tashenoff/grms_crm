'use client';
import React from 'react';
import Modal from './Modal';

export default function LeadModal({ lead, isOpen, onClose }) {
  if (!lead) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Детали заявки #${lead.id}`}
      size="lg"
    >
      <div className="space-y-2 text-gray-800">
        <div><strong>Клиент:</strong> {lead.client_name || 'Не указано'}</div>
        <div><strong>Телефон:</strong> {lead.phone || 'Не указано'}</div>
        <div><strong>Email:</strong> {lead.email || 'Не указано'}</div>
        <div><strong>Источник:</strong> {lead.source}</div>
        <div><strong>Статус:</strong> {lead.status}</div>
        <div><strong>Исполнитель:</strong> {lead.executor_username || 'Не назначен'}</div>
        <div><strong>Сообщение:</strong> <pre className="whitespace-pre-wrap text-sm bg-gray-100 p-2 rounded mt-1">{lead.message || 'Нет сообщения'}</pre></div>
        <div><strong>Дата создания:</strong> {new Date(lead.created_at).toLocaleString('ru-RU')}</div>
        
        {lead.order_details && (
          <div>
            <strong>Детали заказа:</strong> 
            <pre className="whitespace-pre-wrap text-sm bg-gray-100 p-2 rounded mt-1 text-gray-800">
              {lead.order_details}
            </pre>
          </div>
        )}
        
        {lead.total_amount && (
          <div><strong>Сумма заказа:</strong> {lead.total_amount}</div>
        )}
      </div>
    </Modal>
  );
}
