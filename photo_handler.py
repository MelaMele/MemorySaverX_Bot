async function captureAndSendPhoto() {
    // በ Jitsi Meet ውስጥ ያለውን የቪዲዮ ኤለመንት መፈለግ
    const videoElement = document.querySelector('video');
    
    if (!videoElement) {
        alert("❌ ፎቶ ለማንሳት መጀመሪያ መድረኩ መጀመር እና ካሜራዎ መከፈት አለበት!");
        return;
    }

    // ፎቶውን በ 640x360 ሳይዝ ለመቅረጽ ሸራ (Canvas) ማዘጋጀት
    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 360;
    const ctx = canvas.getContext('2d');
    
    // የቪዲዮውን ምስል ወደ ሸራው መቅዳት
    ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    const base64Image = canvas.toDataURL('image/jpeg');

    alert("🔄 ፎቶው እየተነሳ ነው... እባክዎ ይጠብቁ");

    // ወደ አዲሱ የFastAPI ፋይል መላክ
    try {
        let response = await fetch('/api/upload_to_channel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: base64Image })
        });
        
        let result = await response.json();
        if (result.success) {
            alert("🔥 ድንቅ ነው! ፎቶው በቀጥታ ወደ ቴሌግራም ቻናልህ ተለጥፏል!");
        } else {
            alert("❌ ስህተት ተፈጥሯል፦ ቻናሉን ወይም ቦቱን ያረጋግጡ።");
        }
    } catch (err) {
        console.error(err);
        alert("❌ ከሰርቨር ጋር መገናኘት አልተቻለም!");
    }
}
