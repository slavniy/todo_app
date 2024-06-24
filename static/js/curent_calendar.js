function show_all(events){		
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,basicWeek,basicDay'
        },
        events: events,
        editable: true,
        eventLimit: true, // allow "more" link when too many events
        selectable: true,
        selectHelper: true,
        select: function(start, end) {       
            $('#ModalAdd #start').val(moment(start).format('YYYY-MM-DD HH:mm:ss'));
            $('#ModalAdd #end').val(moment(end).format('YYYY-MM-DD HH:mm:ss'));
            $('#ModalAdd').modal('show');
        },
        eventRender: function(event, element) {
            element.bind('dblclick', function() {
                $('#ModalEdit #id').val(event.id);
                $('#ModalEdit #title').val(event.title);
                $('#ModalEdit #color').val(event.color);
                $('#ModalEdit').modal('show');
            });
        },
        eventDrop: function(event, delta, revertFunc) { // si changement de position
            edit(event);

        },
        eventResize: function(event,dayDelta,minuteDelta,revertFunc) { // si changement de longueur
 
            edit(event);
        },
        
        
    });
}


function edit(event){
    start = event.start.format('YYYY-MM-DD HH:mm:ss');
    if(event.end){
        end = event.end.format('YYYY-MM-DD HH:mm:ss');
    }else{
        end = start;
    }
    
    id =  event.id;
    
    
    $.ajax({
     url: 'editEventDate',
     type: "POST",
     data: {'id':id, 'start':start, 'end':end},
     success: function(rep) {
            if(rep == 'OK'){
                                            //alert('Сохранено');
            }else{
                alert('Ошибка сохранения. Попробуйте снова.'); 
            }
        }
    });
}