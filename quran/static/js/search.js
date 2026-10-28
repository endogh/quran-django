document.addEventListener("DOMContentLoaded", function() {
   $("#loading").show(); // Tampilkan loading
   const searchBox = document.getElementById("searchBox");
   const surahContainer = document.getElementById("surahContainer");

   let surahData = [];

   // Fetch data Quran dari PHP ke JSON
   fetch("./data/quran.json")
      .then(response => response.json())
      .then(data => {
         surahData = data.data;
         renderSurahs(surahData);
         $("#loading").hide(); // Sembunyikan loading setelah data selesai dimuat
      });

   // Fungsi untuk menampilkan daftar surah
   function renderSurahs(data) {
      surahContainer.innerHTML = ""; // Hapus konten lama
      data.forEach(surah => {
         const surahCard = `
             <div class="col-md-4 ">
                 <div class="card  h-100">
                     <a href="./surah.php?surah=${surah.number}" class="text-decoration-none">
                         <div  class="card-body ">
                             <div  id="listSurah" class="d-flex align-items-center">
                                 <div class="flex-grow-1 ms-3">${surah.number}-
                                     <strong>${surah.name.transliteration.id}</strong>   {${surah.numberOfVerses}}<br>
                                     <small><i>${surah.name.translation.id}</i></small>
                                 </div>
                                 <div class="flex-grow-5 ms-5 arabic-text">
                                     <h2>${surah.name.short}</h2>
                                 </div>
                             </div>
                         </div>
                     </a>
                 </div>
             </div>
         `;
         surahContainer.innerHTML += surahCard;
      });
   }

   // Event listener untuk live search
   searchBox.addEventListener("input", function() {
      const query = this.value.toLowerCase();
      const filteredSurahs = surahData.filter(surah =>
         surah.name.transliteration.id.toLowerCase().includes(query) ||
         surah.name.translation.id.toLowerCase().includes(query)
      );
      renderSurahs(filteredSurahs);
   });
});