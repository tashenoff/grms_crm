'use client';
import React from 'react';
import Modal from './Modal';
import LeadForm from './LeadForm';

/**
 * Компонент модального окна для редактирования существующей заявки
 * @param {Object} props - Свойства компонента
 * @param {boolean} props.isOpen - Флаг, указывающий, открыто ли модальное окно
 * @param {Function} props.onClose - Функция, вызываемая при закрытии модального окна
 * @param {Object} props.lead - Заявка для редактирования
 * @param {Function} props.onLeadUpdated - Функция, вызываемая после успешного обновления заявки
 * @returns {React.ReactElement}
 */
export default function EditLeadModal({ isOpen, onClose, lead, onLeadUpdated }) {
  if (!lead) return null;

  const handleSubmitSuccess = (result) => {
    onLeadUpdated(result);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Редактирование заявки #${lead.id}`}
      size="lg"
    >
      <LeadForm
        lead={lead}
        onSubmitSuccess={handleSubmitSuccess}
        onCancel={onClose}
      />
    </Modal>
  );
} 