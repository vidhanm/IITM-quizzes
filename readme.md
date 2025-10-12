# IITM Quizzes Platform

A comprehensive quiz management and examination platform designed for IIT Madras students. This application provides an interactive interface for taking quizzes, viewing question papers, and accessing educational content with support for both multiple-choice questions (MCQ) and short answer questions.

## 🚀 Features

- **Interactive Quiz Interface**: Take quizzes with real-time feedback and scoring 
- **Multiple Question Types**: Support for both MCQ and Short Answer questions
- **Subject Organization**: Browse quizzes by subjects and exam types
- **Image Support**: Display questions and options with embedded images
- **Responsive Design**: Modern UI with smooth animations and mobile-friendly interface
- **Real-time Scoring**: Immediate feedback on quiz submissions
- **Mathematical Content**: Support for LaTeX rendering with KaTeX

## 🏗️ Project Structure

```
IITM-quizzes/
├── backend/                 # Flask API server
│   ├── app/
│   │   ├── chat.py         # Chat functionality
│   │   └── models.py       # Data models
│   ├── downloaded_images/   # Question and option images
│   ├── main.py             # Main Flask application
│   ├── database.py         # Database connection and utilities
│   └── requirements.txt    # Python dependencies
├── frontend/               # React TypeScript application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   ├── hooks/          # Custom React hooks
│   │   └── lib/            # Utility functions
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
└── README.md              # This file
```

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework for API development
- **SQLite**: Lightweight database for quiz data storage
- **Flask-CORS**: Cross-origin resource sharing support
- **Pydantic**: Data validation and settings management

### Frontend
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **Radix UI**: Accessible component primitives
- **React Router**: Client-side routing
- **KaTeX**: Mathematical equation rendering
- **React Query**: Server state management

## 🚀 Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8 or higher
- Git

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/vidhanm/IITM-quizzes.git
   cd IITM-quizzes
   ```

2. **Set up the Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
   The Flask server will start on `http://localhost:5000`

3. **Set up the Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The React development server will start on `http://localhost:5173`

4. **Access the Application**
   Open your browser and navigate to `http://localhost:5173`

## 📱 Usage

1. **Select Exam Type**: Choose from available exam types (e.g., "End Term")
2. **Browse Subjects**: Select a subject to view available question papers
3. **Take Quiz**: Click on a question paper to start the quiz
4. **Submit Answers**: Answer questions and submit for immediate scoring
5. **View Results**: Get instant feedback on your performance

## 🔧 Development

### Backend Development
```bash
cd backend
# Start development server
python main.py
```

### Frontend Development
```bash
cd frontend
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📊 Database Schema

The application uses SQLite with the following main tables:
- `courses`: Available courses/subjects
- `question_papers`: Quiz papers and their metadata
- `questions`: Individual questions with types and scoring
- `options`: Multiple choice options for MCQ questions
- `answers`: Answer ranges for short answer questions

## 🎨 UI Components

The frontend uses a comprehensive component library built with:
- **Shadcn/ui**: Modern, accessible UI components
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Radix UI**: Accessible primitives

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The open-source community for the amazing tools and libraries used in this project

---

**Note**: This application is designed specifically for IIT Madras students and contains educational content relevant to their curriculum.
