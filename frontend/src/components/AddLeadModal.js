'use client';
import React from 'react';
import Modal from './Modal';
import LeadForm from './LeadForm';

/**
 * Компонент модального окна для добавления новой заявки
 * @param {Object} props - Свойства компонента
 * @param {boolean} props.isOpen - Флаг, указывающий, открыто ли модальное окно
 * @param {Function} props.onClose - Функция, вызываемая при закрытии модального окна
 * @param {Function} props.onLeadAdded - Функция, вызываемая после успешного добавления заявки
 * @returns {React.ReactElement}
 */
export default function AddLeadModal({ isOpen, onClose, onLeadAdded }) {
  const handleSubmitSuccess = (result) => {
    onLeadAdded(result);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Добавление новой заявки"
      size="lg"
    >
      <LeadForm
        onSubmitSuccess={handleSubmitSuccess}
        onCancel={onClose}
      />
    </Modal>
  );
} 