// @ts-check
import React, { useState, useEffect } from "react";
import { Dialog } from "@headlessui/react";

interface InstructionPopupProps {
  isOpen: boolean;
  onClose: () => void;
}

const InstructionPopup: React.FC<InstructionPopupProps> = ({ isOpen, onClose }) => {
  const [isModalOpen, setIsModalOpen] = useState(isOpen);

  useEffect(() => {
    setIsModalOpen(isOpen);
  }, [isOpen]);

  return (
    <Dialog
      open={isModalOpen}
      onClose={onClose}
      as="div"
      className="fixed inset-0 z-10 overflow-y-auto"
      aria-labelledby="modal-title"
    >
      <div className="flex min-h-screen items-center justify-center">
        <Dialog.Overlay className="fixed inset-0 bg-black opacity-30" />
        <div className="responsive-instruction-box relative rounded-lg bg-slate-200 p-4 shadow-lg">
          <Dialog.Title
            id="modal-title"
            className="mb-4 text-center font-inter text-xl font-bold"
          >
            Welcome to MLMap.xyz!
          </Dialog.Title>
          <Dialog.Description className="text-center font-inter text-gray-700">
            <p>
              Dive into our interactive embedding map to explore the ever-changing
              artificial intelligence landscape and gain valuable insights into key
              features discussed across publications. Uncover new perspectives,
              search for relevant papers, and upload your own abstract to align your
              work with existing conference and feature clusters.
            </p>
            <p className="mt-4">
              <strong>
                Due to hosting costs, support for MLMap.xyz has ended. We hope you
                enjoyed our service!
              </strong>
            </p>
            <p className="mt-4">
              <a
                href="https://github.com/rchalamala/MLMap.xyz"
                target="_blank"
                rel="noopener noreferrer"
                className="text-center font-inter text-blue-500 hover:underline"
              >
                View the source code here.
              </a>
            </p>
          </Dialog.Description>
          <div className="mt-4 flex justify-center">
            <Dialog.Close
              as="button"
              className="rounded-lg bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-600"
            >
              Start Exploring
            </Dialog.Close>
          </div>
          <Dialog.Close
            as="button"
            className="absolute right-2 top-2 text-gray-600 hover:text-gray-800"
            aria-label="Close"
          >
            &#10005;
          </Dialog.Close>
        </div>
      </div>
    </Dialog>
  );
};

export default InstructionPopup;