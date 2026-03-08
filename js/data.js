// ========== InternIQ Dynamic Data ==========

const internshipListings = [
  {
    id: 1,
    company: "Trendyol",
    logo: "🛒",
    position: "Software Engineering Intern",
    location: "İstanbul, Türkiye",
    type: "Hybrid",
    tags: ["Java", "Spring Boot", "Microservices", "Kubernetes"],
    deadline: "2026-04-15",
    description: "Join Trendyol's engineering team to work on scalable e-commerce solutions.",
    matchScore: 92
  },
  {
    id: 2,
    company: "Getir",
    logo: "🚀",
    position: "Backend Developer Intern",
    location: "İstanbul, Türkiye",
    type: "On-site",
    tags: ["Node.js", "MongoDB", "Redis", "Docker"],
    deadline: "2026-04-20",
    description: "Work on real-time delivery optimization systems.",
    matchScore: 87
  },
  {
    id: 3,
    company: "Hepsiburada",
    logo: "🏬",
    position: "Data Science Intern",
    location: "İstanbul, Türkiye",
    type: "Remote",
    tags: ["Python", "TensorFlow", "SQL", "Spark"],
    deadline: "2026-05-01",
    description: "Develop recommendation algorithms and analyze customer behavior.",
    matchScore: 78
  },
  {
    id: 4,
    company: "Peak Games",
    logo: "🎮",
    position: "Game Developer Intern",
    location: "Ankara, Türkiye",
    type: "On-site",
    tags: ["Unity", "C#", "Game Design", "AI"],
    deadline: "2026-04-30",
    description: "Create and optimize mobile game mechanics for millions of users.",
    matchScore: 65
  },
  {
    id: 5,
    company: "Insider",
    logo: "📊",
    position: "Full Stack Developer Intern",
    location: "İstanbul, Türkiye",
    type: "Hybrid",
    tags: ["React", "Go", "PostgreSQL", "AWS"],
    deadline: "2026-04-10",
    description: "Build AI-powered marketing tools used by global brands.",
    matchScore: 95
  },
  {
    id: 6,
    company: "Turkcell",
    logo: "📱",
    position: "AI/ML Intern",
    location: "İstanbul, Türkiye",
    type: "On-site",
    tags: ["Python", "PyTorch", "NLP", "Computer Vision"],
    deadline: "2026-05-15",
    description: "Research and develop AI solutions for telecom industry.",
    matchScore: 83
  }
];

const companyData = [
  {
    name: "Trendyol",
    logo: "🛒",
    industry: "E-Commerce",
    employees: "5,000+",
    rating: 4.2,
    techStack: ["Java", "Kotlin", "React", "Kubernetes", "Kafka", "PostgreSQL"],
    culture: "Fast-paced, innovative, data-driven",
    interviewStyle: "2 technical rounds + 1 HR + system design for senior roles",
    recentNews: "Trendyol expanded to 5 new European markets in 2026."
  },
  {
    name: "Getir",
    logo: "🚀",
    industry: "Quick Commerce",
    employees: "3,000+",
    rating: 3.8,
    techStack: ["Node.js", "React Native", "MongoDB", "Redis", "Docker", "AWS"],
    culture: "Startup mentality, high ownership, rapid iteration",
    interviewStyle: "Coding challenge + 2 technical interviews + culture fit",
    recentNews: "Getir launched its API platform for third-party integrations."
  },
  {
    name: "Insider",
    logo: "📊",
    industry: "MarTech / SaaS",
    employees: "1,200+",
    rating: 4.5,
    techStack: ["React", "Go", "Python", "PostgreSQL", "AWS", "Kubernetes"],
    culture: "Product-focused, global team, continuous learning",
    interviewStyle: "Take-home project + pair programming + behavioral interview",
    recentNews: "Insider named a Leader in Gartner Magic Quadrant 2026."
  }
];

const mockInterviewQuestions = {
  technical: [
    {
      question: "REST API ile GraphQL arasındaki temel farklar nelerdir? Hangi durumda hangisini tercih edersiniz?",
      category: "Backend",
      difficulty: "Medium"
    },
    {
      question: "Big-O notation nedir? Bir binary search algoritmasının time complexity'sini açıklayın.",
      category: "Algorithms",
      difficulty: "Easy"
    },
    {
      question: "React'te Virtual DOM nasıl çalışır? Performansı neden artırır?",
      category: "Frontend",
      difficulty: "Medium"
    },
    {
      question: "Bir e-ticaret sitesinin veritabanı şemasını nasıl tasarlarsınız? Normalization düzeylerini açıklayın.",
      category: "Database",
      difficulty: "Hard"
    },
    {
      question: "CI/CD pipeline nedir? Bir projeye nasıl kurar ve yönetirsiniz?",
      category: "DevOps",
      difficulty: "Medium"
    }
  ],
  behavioral: [
    {
      question: "Bir takım projesinde anlaşmazlık yaşadığınız bir durumu anlatır mısınız? Nasıl çözdünüz?",
      category: "Teamwork",
      difficulty: "Easy"
    },
    {
      question: "Deadline baskısı altında kalite ve hız arasında nasıl denge kurarsınız?",
      category: "Time Management",
      difficulty: "Medium"
    },
    {
      question: "Başarısızlıkla sonuçlanan bir projenizden ne öğrendiniz?",
      category: "Self-Reflection",
      difficulty: "Easy"
    }
  ]
};

const cvSuggestions = [
  { icon: "✅", text: "Teknik becerilerin ilanla %87 oranında eşleşiyor" },
  { icon: "⚠️", text: "\"Docker\" ve \"Kubernetes\" deneyimini eklemeyi düşün — ilanlarda sıkça aranıyor" },
  { icon: "💡", text: "Proje açıklamalarında impact metriklerini belirt (ör: %30 performans artışı)" },
  { icon: "📝", text: "Summary bölümünü pozisyona özel yeniden yaz" },
  { icon: "🎯", text: "ATS uyumluluğu için standart bölüm başlıkları kullan" }
];

const weeklyRoadmap = [
  {
    week: "Hafta 2",
    title: "OpenAI SDK — CV Tailoring Assistant",
    description: "OpenAI API ile ilanları analiz eden ve CV'yi optimize eden akıllı asistan geliştirilecek.",
    tech: "OpenAI SDK, GPT-4"
  },
  {
    week: "Hafta 3",
    title: "CrewAI — Multi-Agent Araştırma Ekibi",
    description: "Araştırmacı, CV uzmanı ve mülakat koçu agentlardan oluşan bir ekip oluşturulacak.",
    tech: "CrewAI, LLM Agents"
  },
  {
    week: "Hafta 4",
    title: "LangGraph — Başvuru Workflow Motoru",
    description: "Başvuru → Hazırlık → Takip akışını yöneten stateful workflow graph'ı inşa edilecek.",
    tech: "LangGraph, State Machines"
  },
  {
    week: "Hafta 5",
    title: "AutoGen — Otonom İlan Tarama Sistemi",
    description: "Otomatik ilan tarayıcı ve bildirim sistemi geliştirilecek.",
    tech: "AutoGen, Web Scraping"
  },
  {
    week: "Hafta 6",
    title: "MCP — Platform Entegrasyonları",
    description: "LinkedIn, Kariyer.net ve Gmail ile doğrudan entegrasyon sağlanacak.",
    tech: "MCP Protocol, API Integration"
  }
];
