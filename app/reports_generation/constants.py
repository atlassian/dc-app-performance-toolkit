
class DCAPTRunType:
	baseline = 'baseline'
	experiment = 'experiment'


DC_APPS_JIRA_TOLERANCE_RANGES = {

	'jmeter_add_comment:open_comment': 0.09,  # 0.083
	'jmeter_add_comment:save_comment': 0.4,  # 0.332
	'jmeter_browse_boards': 0.2,  # 0.17
	'jmeter_browse_projects': 0.04,  # 0.04
	'jmeter_create_issue:fill_and_submit_issue_form': 0.72,  # 0.72
	'jmeter_create_issue:open_quick_create': 0.15,  # 0.12
	'jmeter_edit_issue:open_editor': 0.15,  # 0.13
	'jmeter_edit_issue:save_edit': 0.3,  # 0.28
	'jmeter_login_and_view_dashboard': 0.2,  # 0.2
	'jmeter_search_jql': 0.09,  # 0.083
	'jmeter_view_backlog': 0.15,  # 0.15
	'jmeter_view_dashboard': 0.05,  # 0.03
	'jmeter_view_issue': 0.2,  # 0.17
	'jmeter_view_kanban_board': 0.15,  # 0.15
	'jmeter_view_project_summary': 0.1,  # 0.094
	'jmeter_view_scrum_board': 0.1,  # 0.099

	'selenium_browse_boards_list': 0.04,  # 0.04
	'selenium_browse_projects_list': 0.09,  # 0.078
	'selenium_create_issue': 0.09,  # 0.086
	'selenium_create_issue:fill_and_submit_issue_form': 0.09,  # 0.076
	'selenium_create_issue:fill_and_submit_issue_form:submit_issue_form': 0.03,  # 0.023
	'selenium_create_issue:open_quick_create': 0.09,  # 0.083
	'selenium_edit_issue': 0.1,  # 0.099
	'selenium_edit_issue:open_edit_issue_form': 0.15,  # 0.12
	'selenium_edit_issue:save_edit_issue_form': 0.08,  # 0.065
	'selenium_log_out': 0.5,  # 0.089
	'selenium_login': 0.1,  # 0.092
	'selenium_login:login_and_view_dashboard': 0.1,  # 0.091
	'selenium_login:open_login_page': 0.5,  # 0.079
	'selenium_project_summary': 0.09,  # 0.082
	'selenium_save_comment': 0.09,  # 0.081
	'selenium_save_comment:open_comment_form': 0.1,  # 0.047
	'selenium_save_comment:submit_form': 0.16,  # 0.16
	'selenium_search_jql': 0.1,  # 0.09
	'selenium_view_dashboard': 0.15,  # 0.14
	'selenium_view_issue': 0.15,  # 0.11
	'selenium_view_kanban_board': 0.05,  # 0.037
	'selenium_view_scrum_board': 0.04,  # 0.029
	'selenium_view_scrum_board_backlog': 0.05,  # 0.045
}
CPT_CONFLUENCE_TOLERANCES = {
	'AddPageLabel-Ajax': 0.13,
	'AddPageLabel-Main': 0.15,
	'AddPageLabel-Request': 0.15,
	'AddPageLabel-Total': 0.09,
	'Bots-Capabilities': 0.02,
	'Bots-CheckDetails': 0.08,
	'Bots-Login': 0.07,
	'Bots-Manifest': 0.02,
	'Bots-OpenSearch': 0.13,
	'Bots-ServletStreams': 0.4,  # 1.5/
	'Bots-Status': 0.02,
	'CreateBlog-OpenEditor-Ajax': 0.4,  # 1.7
	'CreateBlog-OpenEditor-Main': 0.22,
	'CreateBlog-OpenEditor-Request': 0.22,
	'CreateBlog-OpenEditor-Total': 0.4,  # 1.46
	'CreateBlog-Poll': 0.1,
	'CreateBlog-Save-Ajax': 0.4,
	'CreateBlog-Save-JSON-Request': 0.4,  # 1.91
	'CreateBlog-Save-Main': 0.4,  # 0.99
	'CreateBlog-Save-MainRequest': 0.06,
	'CreateBlog-Save-Total': 0.4,  # 0.87
	'CreateComments-Blog-Ajax': 0.06,
	'CreateComments-Blog-Main': 0.4,  # 2.82
	'CreateComments-Blog-Request': 0.4,  # 2.82
	'CreateComments-Blog-Total': 0.4,  # 2.19
	'CreateFromTemplate-Popup-Ajax': 0.07,
	'CreateFromTemplate-Popup-Main': 0.15,
	'CreateFromTemplate-Popup-Request': 0.15,
	'CreateFromTemplate-Popup-Total': 0.07,
	'CreatePage-OpenEditor-Ajax': 0.4,  # 2.04
	'CreatePage-OpenEditor-Main': 0.4,  # 1.92
	'CreatePage-OpenEditor-Request': 0.4,  # 1.92
	'CreatePage-OpenEditor-Total': 0.4,  # 1.48
	'CreatePage-Poll': 0.1,
	'CreatePage-Save-Ajax': 0.4,  # 1.06
	'CreatePage-Save-JSONRequest': 0.4,  # 1.75
	'CreatePage-Save-Main': 0.4,  # 1.03
	'CreatePage-Save-MainRequest': 0.05,
	'CreatePage-Save-Total': 0.4,  # 0.95
	'CreatePageComments-Ajax': 0.05,
	'CreatePageComments-Main': 0.4,  # 2.43
	'CreatePageComments-Request': 0.4,  # 2.43
	'CreatePageComments-Total': 0.4,  # 2.2
	'CreateReplyBlogComments-Main': 0.4,  # 2.91
	'CreateReplyBlogComments-Request': 0.4,  # 2.91
	'CreateReplyBlogComments-Total': 0.4,  # 2.91
	'CreateReplyPageComments-Main': 0.4,  # 1.93
	'CreateReplyPageComments-Request': 0.4,  # 1.93
	'CreateReplyPageComments-Total': 0.4,  # 1.93
	'EditPage-Poll': 0.1,
	'EditPage-Quick-Ajax': 0.09,
	'EditPage-Quick-Main': 0.08,
	'EditPage-Quick-Request': 0.08,
	'EditPage-Quick-Total': 0.08,
	'EditPage-SaveChanges-Ajax': 0.09,
	'EditPage-SaveChanges-JSON-DraftRequest': 0.4,  # 2.53
	'EditPage-SaveChanges-Main': 0.4,  # 1.44
	'EditPage-SaveChanges-MainRequest': 0.05,
	'EditPage-SaveChanges-Total': 0.5,  # 1.07
	'EditPage-Slow-Ajax': 0.09,
	'EditPage-Slow-Main': 0.08,
	'EditPage-Slow-Request': 0.08,
	'EditPage-Slow-Total': 0.08,
	'LikeBlog-Ajax': 0.06,
	'LikeBlog-Main': 0.4,  # 3.12
	'LikeBlog-Request': 0.4,  # 3.12
	'LikeBlog-Total': 0.4,  # 2.87
	'LikePage-Ajax': 0.07,
	'LikePage-Main': 0.12,
	'LikePage-Request': 0.12,
	'LikePage-Total': 0.08,
	'Login-Request': 0.4,  # 3.37
	'Login-Total': 0.4,  # 3.37
	'LoginPage-Ajax': 0.02,
	'LoginPage-Main': 0.07,
	'LoginPage-Request': 0.07,
	'LoginPage-Total': 0.07,
	'Logout-Main': 0.4,  # 1.59
	'Logout-PostRequest': 0.4,  # 1.59
	'Logout-Total': 0.4,  # 1.59
	'RestrictPage-Confirm-Main': 0.4,  # 1.8800000000000001,
	'RestrictPage-Confirm-Request': 0.4,  # 1.8800000000000001,
	'RestrictPage-Confirm-Total': 0.4,  # 1.8800000000000001,
	'RestrictPageDialog-Ajax': 0.1,
	'RestrictPageDialog-Main': 0.1,
	'RestrictPageDialog-Request': 0.1,
	'RestrictPageDialog-Total': 0.1,
	'SavePageLabel-Main': 0.4,  # 1.7,
	'SavePageLabel-MainRequest': 0.4,  # 2.25,
	'SavePageLabel-PostRequest': 0.04,
	'SavePageLabel-Total': 0.4,  # 1.7,
	'SearchResults-RecentRequest': 0.07,
	'SearchResults-Request': 0.08,
	'SearchResults-Request-Ajax': 0.17,
	'SearchResults-Request-Main': 0.08,
	'SearchResults-Request-Total': 0.08,
	'UploadAttachments-Ajax': 0.11,
	'UploadAttachments-Main': 0.4,  # 1.05,
	'UploadAttachments-MainRequest': 0.06,
	'UploadAttachments-PostRequest': 0.4,  # 1.24,

	'logout_dom_content_loaded': 0.24,
	'logout_onload': 0.23,
	'open_blog_dom_content_loaded': 0.05,
	'open_blog_onload': 0.07,
	'open_created_page_dom_content_loaded': 0.08,
	'open_created_page_onload': 0.11,
	'open_dashboard_dom_content_loaded': 0.07,
	'open_dashboard_onload': 0.12,
	'open_edited_page_dom_content_loaded': 0.05,
	'open_edited_page_onload': 0.08,
	'open_editor_by_url_dom_content_loaded': 0.08,
	'open_editor_by_url_onload': 0.09,
	'open_editor_dom_content_loaded': 0.06,
	'open_editor_onload': 0.09,
	'open_page_dom_content_loaded': 0.08,
	'open_page_onload': 0.11,
	'open_popular_page_dom_content_loaded': 0.14,
	'open_popular_page_onload': 0.15,
	'open_recently_viewed_dom_content_loaded': 0.05,
	'open_recently_viewed_onload': 0.11

}

DC_APPS_CONFLUENCE_TOLERANCE_RANGES = {
	'jmeter_comment_page': 0.03,
	'jmeter_create_and_edit_page:create_page': 0.03,
	'jmeter_create_and_edit_page:create_page_editor': 0.03,
	'jmeter_create_and_edit_page:edit_page': 0.03,
	'jmeter_create_and_edit_page:open_editor': 0.03,
	'jmeter_create_blog:blog_editor': 0.03,
	'jmeter_create_blog:feel_and_publish': 0.03,
	'jmeter_like_page': 0.03,
	'jmeter_login_and_view_dashboard': 0.03,
	'jmeter_search_cql:recently_viewed': 0.03,
	'jmeter_search_cql:search_results': 0.03,
	'jmeter_upload_attachment': 0.03,
	'jmeter_view_attachment': 0.03,
	'jmeter_view_blog': 0.03,
	'jmeter_view_dashboard': 0.03,
	'jmeter_view_page:open_page': 0.03,

	'selenium_create_comment': 0.03,
	'selenium_create_comment:save_comment': 0.03,
	'selenium_create_comment:write_comment': 0.05,
	'selenium_create_page': 0.05,
	'selenium_create_page:open_create_page_editor': 0.01,
	'selenium_create_page:save_created_page': 0.03,
	'selenium_edit_page': 0.03,
	'selenium_edit_page:open_create_page_editor': 0.03,
	'selenium_edit_page:save_edited_page': 0.03,
	'selenium_log_out': 0.03,
	'selenium_login': 0.03,
	'selenium_login:login_and_view_dashboard': 0.03,
	'selenium_login:open_login_page': 0.03,
	'selenium_view_blog': 0.03,
	'selenium_view_dashboard': 0.01,
	'selenium_view_page': 0.03
}

JPT_TOLERANCE_RANGES_STANDALONE = {
	'View Board': 0.004,
	'View Backlog': 0.007,
	'View Issue': 0.008,
	'View Dashboard': 0.01,
	'Simple searches': 0.0018,
	'Changelog searches': 0.037,
	'Add Comment': 0.01,
	'Create Issue': 0.026,
	'Edit Issue': 0.0084,
	'Project Summary': 0.010,
	'Browse Projects': 0.0065,
	'Browse Boards': 0.007,

	# no tolerance for these actions in JPT
	# 'Full Create Issue': 0.03,
	# 'Full Add Comment': 0.03,
	# 'Full Edit Issue': 0.03
}

JPT_TOLERANCE_RANGES_DATACENTER = {
	'View Board': 0.004,
	'View Backlog': 0.007,
	'View Issue': 0.011,
	'View Dashboard': 0.012,
	'Simple searches': 0.0092,
	'Changelog searches': 0.0459,
	'Add Comment': 0.013,
	'Create Issue': 0.026,
	'Edit Issue': 0.015,
	'Project Summary': 0.0093,
	'Browse Projects': 0.01,
	'Browse Boards': 0.013,
}

DC_APPS_TOLERANCE_FOR_CPT = {
	'jmeter_comment_page': 0.34,
	'jmeter_create_and_edit_page:create_page': 0.33,
	'jmeter_create_and_edit_page:create_page_editor': 0.27,
	'jmeter_create_and_edit_page:edit_page': 0.35,
	'jmeter_create_and_edit_page:open_editor': 0.27,
	'jmeter_create_blog:blog_editor': 0.35,
	'jmeter_create_blog:feel_and_publish': 0.34,
	'jmeter_like_page': 0.32,
	'jmeter_login_and_view_dashboard': 0.35,
	'jmeter_search_cql:recently_viewed': 0.52,
	'jmeter_search_cql:search_results': 0.13,
	'jmeter_upload_attachment': 0.2,
	'jmeter_view_attachment': 0.27,
	'jmeter_view_blog': 0.21,
	'jmeter_view_dashboard': 0.34,
	'jmeter_view_page:open_page': 0.28,

	'selenium_create_comment': 0.2,
	'selenium_create_comment:save_comment': 0.05,
	'selenium_create_comment:write_comment': 0.05,
	'selenium_create_page': 0.05,
	'selenium_create_page:open_create_page_editor': 0.05,
	'selenium_create_page:save_created_page': 0.09,
	'selenium_edit_page': 0.05,
	'selenium_edit_page:open_create_page_editor': 0.05,
	'selenium_edit_page:save_edited_page': 0.09,
	'selenium_log_out': 0.09,
	'selenium_login': 0.05,
	'selenium_login:login_and_view_dashboard': 0.05,
	'selenium_login:open_login_page': 0.05,
	'selenium_view_blog': 0.05,
	'selenium_view_dashboard': 0.05,
	'selenium_view_page': 0.05
}
