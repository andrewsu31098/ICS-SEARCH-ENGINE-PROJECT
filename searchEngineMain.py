from search import SearchEngine
import tkinter as tk 

if __name__ == "__main__":
    ghettoGoogle = SearchEngine()

    def searchButtonEvent(): 
        search_query = searchQueryWidget.get()
        search_results = ghettoGoogle.search(search_query)
        resultsCanvas = tk.Tk()
        if search_results == None: 
            tk.Label(resultsCanvas,text="No results",justify=tk.LEFT).pack(fill='both') 
        else: 
            searchTextBox = tk.Text(resultsCanvas,height=20,width=100)
            searchTextBox.pack(side=tk.LEFT,fill=tk.Y)
            scrollBar = tk.Scrollbar(resultsCanvas)
            scrollBar.pack(side=tk.RIGHT,fill=tk.Y)

            scrollBar.config(command=searchTextBox.yview)
            searchTextBox.config(yscrollcommand=scrollBar.set)

            searchTextBox.tag_config('Link',foreground='blue')
            for i in range(len(search_results)):
                searchTextBox.insert(tk.END,search_results[i][0]+"\n",'Link')
                searchTextBox.insert(tk.END,search_results[i][1]+"\n\n")

    canvas = tk.Tk()
    tk.Label(canvas, text = "Enter search query").grid(row = 0)
    searchQueryWidget = tk.Entry(canvas)
    searchQueryWidget.grid(row=0,column=1)
    
    tk.Button(canvas,text="Quit",command=canvas.quit).grid(row=1,column=0,sticky=tk.W)
    tk.Button(canvas,text="Search",command=searchButtonEvent).grid(row=1,column=0,sticky=tk.W)
    canvas.mainloop() 

    
