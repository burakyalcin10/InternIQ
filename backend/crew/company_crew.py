"""
InternIQ Company Research Crew — CrewAI Implementation

3-agent crew that researches a company and produces
a structured intelligence report for internship candidates.

Agents:
  1. Culture Researcher — company culture, work environment
  2. Tech Analyst — technology stack, engineering practices
  3. Report Writer — synthesizes findings into final report

When OPENAI_API_KEY is not set, falls back to simulated responses.
"""

import os
import json
import yaml
from pathlib import Path

# --- Fallback data for when no API key is available ---
FALLBACK_REPORTS = {
    "ASELSAN": {
        "company_summary": "ASELSAN, Türkiye'nin en büyük savunma elektroniği şirketidir. 1975 yılında kurulan şirket, askeri haberleşme, radar, elektronik harp ve aviyonik sistemleri geliştirmektedir.",
        "culture": "ASELSAN'da mühendislik odaklı, disiplinli bir çalışma kültürü hakimdir. Uzun vadeli projeler üzerinde çalışıldığı için sabır ve derinlemesine teknik bilgi ön plandadır. Stajyerler gerçek projelerde görev alabilir, ancak güvenlik sınıflandırması nedeniyle bazı alanlara erişim kısıtlı olabilir. Mentorluk sistemi güçlüdür ve her stajyere bir kıdemli mühendis eşlik eder.",
        "tech_stack": ["C/C++", "Embedded Linux", "FPGA/VHDL", "Qt Framework", "Python", "MATLAB/Simulink", "RTOS", "Git"],
        "interview_tips": [
            "C/C++ ve pointer mantığı üzerine teknik sorular beklenir",
            "Veri yapıları ve algoritmalar temel düzeyde sorulur",
            "Gömülü sistem ve sinyal işleme bilgisi artı puan",
            "Takım çalışmasını öne çıkaran davranışsal sorular",
            "Son başvuru tarihlerini kaçırmayın — genellikle Mart ayında kapanır"
        ],
        "pros": [
            "Türkiye'nin en prestijli savunma şirketlerinden biri",
            "Gerçek projelerde uygulamalı deneyim",
            "Güçlü mentorluk programı",
            "İş güvencesi yüksek",
            "Başarılı stajyerlere işe alım fırsatı"
        ],
        "cons": [
            "Bürokratik süreçler zaman alabilir",
            "Güvenlik sınıflandırması bazı alanlara erişimi kısıtlar",
            "Ankara dışı lokasyon seçeneği sınırlı",
            "Remote çalışma imkanı yok"
        ],
        "overall_rating": "8.5/10 — Savunma sanayiinde kariyer yapmak isteyenler için mükemmel başlangıç noktası",
        "recommendation": "Gömülü sistemler ve savunma teknolojilerine ilgili stajyerler için kesinlikle önerilir. C/C++ bilginizi güçlendirin ve ASELSAN'ın yaptığı projeleri önceden araştırın."
    },
    "BAYKAR": {
        "company_summary": "BAYKAR, Türkiye'nin insansız hava aracı (İHA) teknolojisinde dünya lideri savunma teknoloji şirketidir. Bayraktar TB2, AKINCI ve Kızılelma projeleriyle tanınır.",
        "culture": "BAYKAR'da startup zihniyetiyle savunma sanayi disiplini bir arada yaşar. Hızlı karar alma, yenilikçilik ve yüksek sahiplenme beklenir. Stajyerler gerçek Ar-Ge projelerinde aktif rol alır. Çalışma saatleri yoğun olabilir ama öğrenme hızı çok yüksektir. Genç ve dinamik bir mühendislik ekibi bulunur.",
        "tech_stack": ["Python", "C++", "ROS/ROS2", "OpenCV", "TensorFlow/PyTorch", "Embedded Linux", "MATLAB", "Docker", "Git"],
        "interview_tips": [
            "Python ve algoritma soruları yoğun şekilde sorulur",
            "Görüntü işleme ve makine öğrenmesi projeleri anlatabilmelisiniz",
            "ROS bilgisi büyük artı puan",
            "Motivasyon ve BAYKAR projelerine olan ilginiz değerlendirilir",
            "GitHub profilinizdeki projeler önemli — aktif profil olsun"
        ],
        "pros": [
            "Dünya çapında tanınan İHA projelerinde çalışma fırsatı",
            "Yapay zeka ve otonom sistemlerde son teknoloji deneyim",
            "Yüksek işe alım oranı — başarılı stajyerler genellikle teklif alır",
            "Genç ve dinamik ekip",
            "Hızlı kariyer gelişimi"
        ],
        "cons": [
            "Çalışma saatleri yoğun olabilir",
            "İstanbul trafiğinde ulaşım zorlu olabilir",
            "Güvenlik izni süreci uzun sürebilir",
            "İş-yaşam dengesi zorlu olabilir"
        ],
        "overall_rating": "9/10 — Otonom sistemler ve AI alanında kariyer yapmak isteyenler için Türkiye'nin en iyi fırsatı",
        "recommendation": "Yapay zeka, görüntü işleme veya robotik alanında uzmanlaşmak istiyorsanız BAYKAR mükemmel bir seçim. Python ve OpenCV projelerinizi güçlendirin, ROS öğrenin."
    },
}

# Generic fallback for unknown companies
GENERIC_FALLBACK = {
    "company_summary": "{company} hakkında detaylı bilgi toplanıyor. Bu şirket Türkiye teknoloji ve savunma sektöründe faaliyet göstermektedir.",
    "culture": "Şirket kültürü hakkında yapay zeka analizi gerçekleştirildi. Bu şirket mühendislik odaklı bir çalışma ortamı sunmaktadır. Stajyerler mentörlük programlarından faydalanabilir ve gerçek projelerde deneyim kazanabilir.",
    "tech_stack": ["Python", "Java", "C++", "React", "Docker", "Git"],
    "interview_tips": [
        "Algoritma ve veri yapıları bilgisini güçlendirin",
        "Şirketin faaliyet alanıyla ilgili projeler hazırlayın",
        "GitHub profilinizi güncel tutun",
        "Teknik mülakat için LeetCode pratikleri yapın",
        "Şirketi önceden detaylı araştırın"
    ],
    "pros": [
        "Sektörde deneyim kazanma fırsatı",
        "Profesyonel network oluşturma imkanı",
        "Gerçek projelerde çalışma deneyimi"
    ],
    "cons": [
        "Staj süresi sınırlı olabilir",
        "Pozisyonlar için yoğun rekabet"
    ],
    "overall_rating": "7/10 — Staj deneyimi için değerlendirilebilir",
    "recommendation": "Temel teknik becerilerinizi güçlendirin ve şirkete özel projeler hazırlayarak başvurunuzu farklılaştırın."
}


def get_fallback_report(company_name: str) -> dict:
    """Return pre-built report when no API key is available."""
    if company_name.upper() in FALLBACK_REPORTS:
        return FALLBACK_REPORTS[company_name.upper()]

    # Generate generic report with company name filled in
    report = {}
    for key, value in GENERIC_FALLBACK.items():
        if isinstance(value, str):
            report[key] = value.replace("{company}", company_name)
        else:
            report[key] = value
    return report


def run_crew(company_name: str) -> dict:
    """
    Main entry point: kicks off the CrewAI crew to research a company.
    Falls back to simulated data if OPENAI_API_KEY is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key or api_key == "your_openai_key_here":
        print(f"[CrewAI] No API key — using fallback for '{company_name}'")
        return {
            "status": "fallback",
            "company": company_name,
            "report": get_fallback_report(company_name),
            "message": "API key bulunamadı. Simüle rapor döndürüldü. Gerçek AI analizi için OPENAI_API_KEY ekleyin."
        }

    # --- Real CrewAI execution ---
    try:
        from crewai import Agent, Task, Crew, Process

        config_dir = Path(__file__).parent / "config"

        with open(config_dir / "agents.yaml", "r", encoding="utf-8") as f:
            agents_config = yaml.safe_load(f)

        with open(config_dir / "tasks.yaml", "r", encoding="utf-8") as f:
            tasks_config = yaml.safe_load(f)

        # Create Agents
        culture_researcher = Agent(
            role=agents_config["culture_researcher"]["role"].format(company=company_name),
            goal=agents_config["culture_researcher"]["goal"].format(company=company_name),
            backstory=agents_config["culture_researcher"]["backstory"].format(company=company_name),
            verbose=True,
            allow_delegation=False,
        )

        tech_analyst = Agent(
            role=agents_config["tech_analyst"]["role"].format(company=company_name),
            goal=agents_config["tech_analyst"]["goal"].format(company=company_name),
            backstory=agents_config["tech_analyst"]["backstory"].format(company=company_name),
            verbose=True,
            allow_delegation=False,
        )

        report_writer = Agent(
            role=agents_config["report_writer"]["role"].format(company=company_name),
            goal=agents_config["report_writer"]["goal"].format(company=company_name),
            backstory=agents_config["report_writer"]["backstory"].format(company=company_name),
            verbose=True,
            allow_delegation=False,
        )

        # Create Tasks
        culture_task = Task(
            description=tasks_config["culture_research_task"]["description"].format(company=company_name),
            expected_output=tasks_config["culture_research_task"]["expected_output"],
            agent=culture_researcher,
        )

        tech_task = Task(
            description=tasks_config["tech_analysis_task"]["description"].format(company=company_name),
            expected_output=tasks_config["tech_analysis_task"]["expected_output"],
            agent=tech_analyst,
        )

        report_task = Task(
            description=tasks_config["compile_report_task"]["description"].format(company=company_name),
            expected_output=tasks_config["compile_report_task"]["expected_output"],
            agent=report_writer,
        )

        # Create and Kickoff Crew
        company_crew = Crew(
            agents=[culture_researcher, tech_analyst, report_writer],
            tasks=[culture_task, tech_task, report_task],
            process=Process.sequential,
            verbose=True,
        )

        result = company_crew.kickoff(inputs={"company": company_name})

        # Parse the result
        try:
            report = json.loads(str(result))
        except json.JSONDecodeError:
            report = {
                "company_summary": str(result),
                "culture": "AI tarafından üretilen rapor — detaylar özet bölümünde.",
                "tech_stack": [],
                "interview_tips": [],
                "pros": [],
                "cons": [],
                "overall_rating": "AI analizi tamamlandı",
                "recommendation": str(result)
            }

        return {
            "status": "success",
            "company": company_name,
            "report": report,
            "message": "CrewAI analizi tamamlandı."
        }

    except Exception as e:
        print(f"[CrewAI] Error: {e}")
        return {
            "status": "fallback",
            "company": company_name,
            "report": get_fallback_report(company_name),
            "message": f"CrewAI hatası: {str(e)}. Fallback rapor döndürüldü."
        }
